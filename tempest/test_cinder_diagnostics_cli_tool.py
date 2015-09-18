# Copyright 2013 IBM Corp.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock
import time
import subprocess
import socket
import sys
import shutil
import paramiko
import os
import json
#from tempest.api.volume import base
from six.moves import configparser
from tempest.tests import base
from tempest import test
from tempest import config
import tempest_lib.cli.output_parser as table_output_parser
from cinderdiags.ssh_client import Client
import cinderdiags.main as cli
import cinderdiags.pkg_checks as pkg_checks
import cinderdiags.constant as constant


class CinderDiagnostics3PARCliToolTest(base.TestCase):

    ''' Test case class for all 3PAR cinder Diagnostics CLI Tool '''

    cinder_config_file = "cinder.conf"

    @classmethod
    def resource_setup(cls):
        super(CinderDiagnostics3PARCliToolTest, cls).resource_setup()

    def setUp(self):

        super(CinderDiagnostics3PARCliToolTest, self).setUp()

        self._remove_file(self.cinder_config_file)

        # 3par FC section
        cli_dict = {}
        cli_dict["CINDER_TEST_NODE"] = self._get_default_cli_conf_section(
            "cinder")
        cli_dict["NOVA_TEST_NODE"] = self._get_default_cli_conf_section("nova")

        # Create cinder.conf
        self._create_config(constant.TEST_CLI_CONFIG, cli_dict)

        self.mock_instances = []

    def tearDown(self):
        # Remove all the packages
        for instance in self.mock_instances:
            instance.stop()

        self._remove_file(self.cinder_config_file)

        self._remove_file(constant.TEST_CLI_CONFIG)

        super(CinderDiagnostics3PARCliToolTest, self).tearDown()

    @test.attr(type="gate")
    def test_diags_cli_check_array_command(self):
        ''' Test cinder diagnostic cli tool check array command when all the configuration values of 3par array are correct in cinde.conf '''

        # Mock paramiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file)

        # create cinder config,conf file and add 3par ISCSI section
        cinder_dict = {}
        # 3par ISCSI section
        section_name, values = self._get_default_3par_iscsi_cinder_conf_section()
        cinder_dict[section_name] = values

        # 3par FC section
        section_name1, valuess = self._get_default_3par_fc_cinder_conf_section()
        cinder_dict[section_name1] = valuess

        # Create cinder.conf
        self._create_config(self.cinder_config_file, cinder_dict)

        # Execute the CLI commnad
        command_arvgs = ['options-check', "-test"]
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0, cli_exit_value)
        self.assertEqual(len(output), 2)

        cli_exit_value, json_cli_output = self._execute_cli_command(
            command_arvgs, True)
        self.assertEqual(0, cli_exit_value)
        self.assertEqual(output, json_cli_output)

        self.assertEqual(len(output), 2)

        for row in output:
            self.assertEqual('CINDER_TEST_NODE', row['Node'])
            self.assertEqual('pass', row['CPG'])
            self.assertEqual('pass', row['Credentials'])
            self.assertEqual('pass', row['WS API'])
            if row['Backend Section'] == '3PAR-SLEEPYKITTY-FC':
                self.assertEqual('N/A', row['iSCSI IP(s)'])
            else:
                self.assertEqual('pass', row['iSCSI IP(s)'])

    @test.attr(type="gate")
    def test_check_array_command_for_specific_array_name(self):
        ''' Test cinder diagnostic cli tool check array command for specific array name '''

        self._mock_get_file(self.cinder_config_file)
        cinder_dict = {}
        # 3par ISCSI section
        section_name, values = self._get_default_3par_iscsi_cinder_conf_section()
        cinder_dict[section_name] = values

        # 3par FC section
        section_name1, valuess = self._get_default_3par_fc_cinder_conf_section()
        cinder_dict[section_name1] = valuess

        # Create cinder.conf
        self._create_config(self.cinder_config_file, cinder_dict)

        command_arvgs = [
            'options-check',
            '-test',
            "-backend-section",
            '3PAR-SLEEPYKITTY-FC']
        cli_exit_value, output = self._execute_cli_command(command_arvgs)
        self.assertEqual(0, cli_exit_value)
        self.assertEqual('3PAR-SLEEPYKITTY-FC', output[0]['Backend Section'])

    def test_check_array_command_with_wrong_arrayname(self):
        ''' Test cinder diagnostic cli tool check array command when wrong array name is given in the command '''

        self._mock_get_file(self.cinder_config_file)
        # create cinder config,conf file and add 3par ISCSI section
        cinder_dict = {}
        # 3par ISCSI section
        section_name, values = self._get_default_3par_iscsi_cinder_conf_section()
        cinder_dict[section_name] = values

        # 3par FC section
        section_name1, valuess = self._get_default_3par_fc_cinder_conf_section()
        cinder_dict[section_name1] = valuess

        # Create cinder.conf
        self._create_config(self.cinder_config_file, cinder_dict)

        # Execute the CLI commnad
        command_arvgs = [
            'options-check',
            '-test',
            "-backend-section",
            'InvalidArrayName']
        cli_exit_value, output = self._execute_cli_command(command_arvgs)
        self.assertEqual(1, cli_exit_value)
        self.assertEqual(len(output), 0)

    @test.attr(type="gate")
    def test_diags_cli_check_array_command_for_bad_ws_api(self):
        ''' Test cinder diagnostic cli tool check array command when the ws api value of 3par array in cinder.conf is wrong '''

        # Mock paramiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file)

        # create cinder config,conf file and add 3par ISCSI section
        cinder_dict = {}
        # 3par ISCSI section
        iscsi_section_name, iscsi_values = self._get_default_3par_iscsi_cinder_conf_section()
        iscsi_values['hp3par_api_url'] = 'http://bad.ws.url:8080/api/v1'
        cinder_dict[iscsi_section_name] = iscsi_values

        # 3par FC section
        fc_section_name, fc_values = self._get_default_3par_fc_cinder_conf_section()
        cinder_dict[fc_section_name] = fc_values

        # Create cinder.conf
        self._create_config(self.cinder_config_file, cinder_dict)

        # Execute the CLI commnad
        command_arvgs = ['options-check', "-test"]
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0, cli_exit_value)
        self.assertEqual(len(output), 2)

        for row in output:
            if row['Backend Section'] == iscsi_section_name:
                self.assertEqual('CINDER_TEST_NODE', row['Node'])
                self.assertEqual('unknown', row['CPG'])
                self.assertEqual('unknown', row['Credentials'])
                self.assertEqual('fail', row['WS API'])
                self.assertEqual('unknown', row['iSCSI IP(s)'])
            else:
                self.assertEqual('CINDER_TEST_NODE', row['Node'])
                self.assertEqual('pass', row['CPG'])
                self.assertEqual('pass', row['Credentials'])
                self.assertEqual('pass', row['WS API'])
                self.assertEqual('N/A', row['iSCSI IP(s)'])

        cli_exit_value, json_cli_output = self._execute_cli_command(
            command_arvgs, True)
        self.assertEqual(0, cli_exit_value)
        self.assertEqual(output, json_cli_output)

    @test.attr(type="gate")
    def test_diags_cli_check_array_command_for_wrong_credential(self):
        ''' Test cinder diagnostic cli tool check array command when the credentials of 3par array in cinder.conf is wrong '''

        # Mock paramiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file)

        # create cinder config,conf file and add 3par ISCSI section
        cinder_dict = {}
        # 3par ISCSI section
        iscsi_section_name, iscsi_values = self._get_default_3par_iscsi_cinder_conf_section()
        cinder_dict[iscsi_section_name] = iscsi_values

        # 3par FC section
        fc_section_name, fc_values = self._get_default_3par_fc_cinder_conf_section()
        fc_values['hp3par_username'] = 'baduser'
        fc_values['hp3par_password'] = 'badpass'
        cinder_dict[fc_section_name] = fc_values

        # Create cinder.conf
        self._create_config(self.cinder_config_file, cinder_dict)

        # Execute the CLI commnad
        command_arvgs = ['options-check', "-test"]
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0, cli_exit_value)
        self.assertEqual(len(output), 2)

        for row in output:
            if row['Backend Section'] == iscsi_section_name:
                self.assertEqual('CINDER_TEST_NODE', row['Node'])
                self.assertEqual('pass', row['CPG'])
                self.assertEqual('pass', row['Credentials'])
                self.assertEqual('pass', row['WS API'])
                self.assertEqual('pass', row['iSCSI IP(s)'])
            else:
                self.assertEqual('CINDER_TEST_NODE', row['Node'])
                self.assertEqual('unknown', row['CPG'])
                self.assertEqual('fail', row['Credentials'])
                self.assertEqual('pass', row['WS API'])
                self.assertEqual('N/A', row['iSCSI IP(s)'])

    @test.attr(type="gate")
    def test_diags_cli_check_array_command_for_bad_CPG(self):
        ''' Test cinder diagnostic cli tool check array command when the cpg value of 3par array in cinder.conf is wrong '''

        # Mock paramiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file)

        # create cinder config,conf file and add 3par ISCSI section
        cinder_dict = {}
        # 3par ISCSI section
        iscsi_section_name, iscsi_values = self._get_default_3par_iscsi_cinder_conf_section()
        iscsi_values['hp3par_cpg'] = 'badCPG'
        cinder_dict[iscsi_section_name] = iscsi_values

        # 3par FC section
        fc_section_name, fc_values = self._get_default_3par_fc_cinder_conf_section()
        fc_values['hp3par_username'] = 'baduser'
        fc_values['hp3par_password'] = 'testpass'
        cinder_dict[fc_section_name] = fc_values

        # Create cinder.conf
        self._create_config(self.cinder_config_file, cinder_dict)

        # Execute the CLI commnad
        command_arvgs = ['options-check', "-test"]
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0, cli_exit_value)
        self.assertEqual(len(output), 2)

        for row in output:
            if row['Backend Section'] == iscsi_section_name:
                self.assertEqual('CINDER_TEST_NODE', row['Node'])
                self.assertEqual('fail', row['CPG'])
                self.assertEqual('pass', row['Credentials'])
                self.assertEqual('pass', row['WS API'])
                self.assertEqual('pass', row['iSCSI IP(s)'])
            else:
                self.assertEqual('CINDER_TEST_NODE', row['Node'])
                self.assertEqual('unknown', row['CPG'])
                self.assertEqual('fail', row['Credentials'])
                self.assertEqual('pass', row['WS API'])
                self.assertEqual('N/A', row['iSCSI IP(s)'])

    @test.attr(type="gate")
    def test_diags_cli_check_array_command_for_one_bad_CPG(self):
        """Test cinder diagnostic cli tool check array command when the cpg
        value of 3par array in cinder.conf is wrong."""

        # Mock paramiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file)

        # create cinder config,conf file and add 3par ISCSI section
        cinder_dict = {}
        # 3par ISCSI section
        iscsi_section_name, iscsi_values = \
            self._get_default_3par_iscsi_cinder_conf_section()
        iscsi_values['hp3par_cpg'] = 'testCPG,badCPG'
        cinder_dict[iscsi_section_name] = iscsi_values

        # 3par FC section
        fc_section_name, fc_values = \
            self._get_default_3par_fc_cinder_conf_section()
        fc_values['hp3par_username'] = 'baduser'
        fc_values['hp3par_password'] = 'testpass'
        cinder_dict[fc_section_name] = fc_values

        # Create cinder.conf
        self._create_config(self.cinder_config_file, cinder_dict)

        # Execute the CLI commnad
        command_arvgs = ['options-check', "-test"]
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0, cli_exit_value)
        self.assertEqual(len(output), 2)

        for row in output:
            if row['Backend Section'] == iscsi_section_name:
                self.assertEqual('CINDER_TEST_NODE', row['Node'])
                self.assertEqual('fail', row['CPG'])
                self.assertEqual('pass', row['Credentials'])
                self.assertEqual('pass', row['WS API'])
                self.assertEqual('pass', row['iSCSI IP(s)'])
            else:
                self.assertEqual('CINDER_TEST_NODE', row['Node'])
                self.assertEqual('unknown', row['CPG'])
                self.assertEqual('fail', row['Credentials'])
                self.assertEqual('pass', row['WS API'])
                self.assertEqual('N/A', row['iSCSI IP(s)'])

    @test.attr(type="gate")
    def test_diags_cli_check_array_command_for_wrong_iscsi_IP(self):
        ''' Test cinder diagnostic cli tool check array command when the ISCSI IP of 3par array in cinder.conf is wrong '''

        # Mock paramiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file)

        # create cinder config,conf file and add 3par ISCSI section
        cinder_dict = {}
        # 3par ISCSI section
        iscsi_section_name, iscsi_values = self._get_default_3par_iscsi_cinder_conf_section()

        iscsi_values['hp3par_iscsi_ips'] = '10.20.15.11:3260'
        cinder_dict[iscsi_section_name] = iscsi_values

        # 3par FC section
        fc_section_name, fc_values = self._get_default_3par_fc_cinder_conf_section()
        fc_values['hp3par_cpg'] = 'badCPG'
        cinder_dict[fc_section_name] = fc_values

        # Create cinder.conf
        self._create_config(self.cinder_config_file, cinder_dict)

        # Execute the CLI commnad
        command_arvgs = ['options-check', "-test"]
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0, cli_exit_value)
        self.assertEqual(len(output), 2)

        for row in output:
            if row['Backend Section'] == iscsi_section_name:
                self.assertEqual('CINDER_TEST_NODE', row['Node'])
                self.assertEqual('pass', row['CPG'])
                self.assertEqual('pass', row['Credentials'])
                self.assertEqual('pass', row['WS API'])
                self.assertEqual('fail', row['iSCSI IP(s)'])
            else:
                self.assertEqual('CINDER_TEST_NODE', row['Node'])
                self.assertEqual('fail', row['CPG'])
                self.assertEqual('pass', row['Credentials'])
                self.assertEqual('pass', row['WS API'])
                self.assertEqual('N/A', row['iSCSI IP(s)'])

    @test.attr(type="gate")
    def test_diags_cli_check_array_command_for_wrong_hp3pardriver(self):
        ''' Test cinder diagnostic cli tool check array command when the volume driver value of 3par array in cinder.conf is wrong '''

        self._mock_exec_command({'locate': None})
        # Mock paramiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file)

        # create cinder config,conf file and add 3par ISCSI section
        cinder_dict = {}
        # 3par ISCSI section
        iscsi_section_name, iscsi_values = self._get_default_3par_iscsi_cinder_conf_section()

        iscsi_values[
            'volume_driver'] = 'cinder.volume.drivers.san.hp.hp_3par_iscsi.HP3PARWrongDriver'
        cinder_dict[iscsi_section_name] = iscsi_values

        # 3par FC section
        fc_section_name, fc_values = self._get_default_3par_fc_cinder_conf_section()
        fc_values[
            'volume_driver'] = 'cinder.volume.drivers.san.hp.hp_3par_fc.HP3PARWrongDriver'
        cinder_dict[fc_section_name] = fc_values

        # Create cinder.conf
        self._create_config(self.cinder_config_file, cinder_dict)

        # Execute the CLI commnad
        command_arvgs = ['options-check', "-test"]
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0, cli_exit_value)
        self.assertEqual(len(output), 2)

        for row in output:
            if row['Backend Section'] == iscsi_section_name:
                self.assertEqual('CINDER_TEST_NODE', row['Node'])
                self.assertEqual('pass', row['CPG'])
                self.assertEqual('pass', row['Credentials'])
                self.assertEqual('pass', row['WS API'])
                self.assertEqual('pass', row['iSCSI IP(s)'])
                self.assertEqual('fail', row['Driver'])
            else:
                self.assertEqual('CINDER_TEST_NODE', row['Node'])
                self.assertEqual('pass', row['CPG'])
                self.assertEqual('pass', row['Credentials'])
                self.assertEqual('pass', row['WS API'])
                self.assertEqual('N/A', row['iSCSI IP(s)'])
                self.assertEqual('fail', row['Driver'])

    @test.attr(type="gate")
    def test_diags_cli_check_array_command_for_wrong_hp3pardriver(self):
        ''' Test cinder diagnostic cli tool check array command when the volume driver value of 3par array in cinder.conf is correct '''

        self._mock_exec_command(
            {
                'locate hp_3par_iscsi': '/opt/stack/cinder/cinder/volume/drivers/san/hp/hp_3par_iscsi.py',
                'locate hp_3par_fc': '/opt/stack/cinder/cinder/volume/drivers/san/hp/hp_3par_fc.py'},
            self.cinder_config_file)

        # create cinder config,conf file and add 3par ISCSI section
        cinder_dict = {}
        # 3par ISCSI section
        iscsi_section_name, iscsi_values = self._get_default_3par_iscsi_cinder_conf_section()
        cinder_dict[iscsi_section_name] = iscsi_values

        # 3par FC section
        fc_section_name, fc_values = self._get_default_3par_fc_cinder_conf_section()
        cinder_dict[fc_section_name] = fc_values

        # Create cinder.conf
        self._create_config(self.cinder_config_file, cinder_dict)

        # Execute the CLI commnad
        command_arvgs = ['options-check', "-test"]
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0, cli_exit_value)
        self.assertEqual(len(output), 2)

        for row in output:
            if row['Backend Section'] == iscsi_section_name:
                self.assertEqual('CINDER_TEST_NODE', row['Node'])
                self.assertEqual('pass', row['CPG'])
                self.assertEqual('pass', row['Credentials'])
                self.assertEqual('pass', row['WS API'])
                self.assertEqual('pass', row['iSCSI IP(s)'])
                self.assertEqual('pass', row['Driver'])
            else:
                self.assertEqual('CINDER_TEST_NODE', row['Node'])
                self.assertEqual('pass', row['CPG'])
                self.assertEqual('pass', row['Credentials'])
                self.assertEqual('pass', row['WS API'])
                self.assertEqual('N/A', row['iSCSI IP(s)'])
                self.assertEqual('pass', row['Driver'])

    @test.attr(type="gate")
    def test_diags_check_all_packages_installed_with_supported_version_on_ubuntu(
            self):
        ''' Test cinder diagnostic cli tool check software command for all the packages with supported version on ubuntu operating system'''

        command_arvgs = ['software-check', '-test']

        # Mock paramiko ssh client to return cinder file we want
        self._mock_exec_command(
            {
                'cat /etc/*release': 'ID_LIKE=debian',
                'sysfsutils': "install ok installed 2.2.0",
                'hp3parclient': "hp3parclient (3.2.2)",
                'sg3-utils': "install ok installed 2.2.0",
            })
        # Execute the CLI commnad
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0, cli_exit_value)
        self.assertEqual(len(output), 3)

        for row in output:
            self.assertEqual("pass", row['Installed'])
            self.assertEqual("pass", row['Version'])

    @test.attr(type="gate")
    def test_diags_check_all_packages_installed_with_supported_version_on_suse(
            self):
        ''' Test cinder diagnostic cli tool check software command for all the packages with supported version SUSE operating system'''

        command_arvgs = ['software-check', '-test']

        # Mock paramiko ssh client to return cinder file we want
        self._mock_exec_command(
            {
                'cat /etc/*release': 'ID_LIKE=suse',
                'sysfsutils': "Installed: Yes  Version: 2.2.0",
                'hp3parclient': "hp3parclient (3.2.2)",
                'sg3-utils': "Installed: Yes  Version: 2.2.0",
            })
        # Execute the CLI commnad
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0, cli_exit_value)
        self.assertEqual(len(output), 3)

        for row in output:
            self.assertEqual("pass", row['Installed'])
            self.assertEqual("pass", row['Version'])

    @test.attr(type="gate")
    def test_diags_check_all_packages_not_installed_with_supported_version_on_suse(
            self):
        ''' Test cinder diagnostic cli tool check software command for all the packages with supported version SUSE operating system'''

        command_arvgs = ['software-check', '-test']

        # Mock paramiko ssh client to return cinder file we want
        self._mock_exec_command(
            {
                'cat /etc/*release': 'ID_LIKE=suse',
                'sysfsutils': "package 'sysfsutils' not found",
                'hp3parclient': "",
                'sg3-utils': "package 'sg3-utils' not found",
            })
        # Execute the CLI commnad
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0, cli_exit_value)
        self.assertEqual(len(output), 3)

        for row in output:
            self.assertEqual("fail", row['Installed'])
            self.assertEqual("N/A", row['Version'])

    @test.attr(type="gate")
    def test_diags_check_all_packages_installed_with_not_supported_version_on_suse(
            self):
        ''' Test cinder diagnostic cli tool check software command for all the packages with supported version SUSE operating system'''

        command_arvgs = ['software-check', '-test']

        # Mock paramiko ssh client to return cinder file we want
        self._mock_exec_command(
            {
                'cat /etc/*release': 'ID_LIKE=suse',
                'sysfsutils': "Installed: Yes  Version: 1.2.0",
                'hp3parclient': "hp3parclient (1.2.2)",
                'sg3-utils': "Installed: Yes  Version: 1.2.0",
            })
        # Execute the CLI commnad
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0, cli_exit_value)
        self.assertEqual(len(output), 3)

        for row in output:
            self.assertEqual("pass", row['Installed'])
            self.assertEqual("fail", row['Version'])

    @test.attr(type="gate")
    def test_diags_check_all_packages_installed_with_supported_version_on_centos(
            self):
        ''' Test cinder diagnostic cli tool check software command for all the packages with supported version centos operating system '''

        command_arvgs = ['software-check', '-test']

        # Mock paramiko ssh client to return cinder file we want
        self._mock_exec_command(
            {
                'cat /etc/*release': 'ID_LIKE=rhel fedora',
                'sysfsutils': "Installed Packages sysfsutils.x86_64  2.2.2",
                'hp3parclient': "hp3parclient (3.2.2)",
                'sg3-utils': "Installed Packages sg3-utils.x86_64  2.2.2",
            })
        # Execute the CLI commnad
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0, cli_exit_value)
        self.assertEqual(len(output), 3)

        for row in output:
            self.assertEqual("pass", row['Installed'])
            self.assertEqual("pass", row['Version'])

    @test.attr(type="gate")
    def test_diags_check_all_packages_not_installed_with_supported_version_on_centos(
            self):
        ''' Test cinder diagnostic cli tool check software command for all the packages with supported version centos operating system '''

        command_arvgs = ['software-check', '-test']

        # Mock paramiko ssh client to return cinder file we want
        self._mock_exec_command(
            {
                'cat /etc/*release': 'ID_LIKE=rhel fedora',
                'sysfsutils': "Error: No matching Packages to list",
                'hp3parclient': "",
                'sg3-utils': "Error: No matching Packages to list",
                'sg3_utils': "Error: No matching Packages to list"
            })
        # Execute the CLI commnad
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0, cli_exit_value)
        self.assertEqual(len(output), 3)

        for row in output:
            self.assertEqual("fail", row['Installed'])
            self.assertEqual("N/A", row['Version'])

    @test.attr(type="gate")
    def test_diags_check_all_packages_installed_with_unsupported_version_on_centos(
            self):
        ''' Test cinder diagnostic cli tool check software command for all the packages with supported version centos operating system '''

        command_arvgs = ['software-check', '-test']

        # Mock paramiko ssh client to return cinder file we want
        self._mock_exec_command(
            {
                'cat /etc/*release': 'ID_LIKE=rhel fedora',
                'sysfsutils': "Installed Packages sysfsutils.x86_64  1.2.2",
                'hp3parclient': "hp3parclient (1.2.2)",
                'sg3-utils': "Installed Packages sg3-utils.x86_64  1.2.2",
            })
        # Execute the CLI commnad
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0, cli_exit_value)
        self.assertEqual(len(output), 3)

        for row in output:
            self.assertEqual("pass", row['Installed'])
            self.assertEqual("fail", row['Version'])

    @test.attr(type="gate")
    def test_diags_sysfsutils_package_installed_with_supported_version(self):
        ''' Test cinder diagnostic cli tool check software command for sysfsutils package with supported version '''

        command_arvgs = [
            'software-check',
            '-software',
            "sysfsutils",
            '--package-min-version',
            '1.3',
            '-service',
            'nova',
            '-test']
        ssh_mocked_response = {
            'cat /etc/*release': 'ID_LIKE=debian',
            'sysfsutils': "install ok installed 2.2.0"}
        # Excecutes the check software command that needs to be tested and
        # evaluates the output
        self._check_software_package(
            'sysfsutils', command_arvgs, ssh_mocked_response)

    @test.attr(type="gate")
    def test_diags_sysfsutils_package_installed_with_unsupported_version(self):
        ''' Test cinder diagnostic cli tool check software command for sysfsutils package with unsupported version '''

        command_arvgs = [
            'software-check',
            '-software',
            "sysfsutils",
            '--package-min-version',
            '2.0',
            '-service',
            'nova',
            '-test']
        ssh_mocked_response = {
            'cat /etc/*release': 'ID_LIKE=debian',
            'sysfsutils': "install ok installed 1.0 "}
        # Excecutes the check software command that needs to be tested and
        # evaluates the output
        self._check_software_package(
            'sysfsutils',
            command_arvgs,
            ssh_mocked_response,
            "pass",
            "fail")

    @test.attr(type="gate")
    def test_diags_sysfsutils_package_not_installed(self):
        ''' Test cinder diagnostic cli tool check software command for non-existent sysfsutils package '''

        command_arvgs = [
            'software-check',
            '-software',
            "sysfsutils",
            '--package-min-version',
            '2.0',
            '-service',
            'nova',
            '-test']
        ssh_mocked_response = {
            'cat /etc/*release': 'ID_LIKE=debian',
            'dpkg-query': 'no packages found matching  sysfsutils',
            'grep sysfsutils': ""}
        # Excecutes the check software command that needs to be tested and
        # evaluates the output
        self._check_software_package(
            'sysfsutils',
            command_arvgs,
            ssh_mocked_response,
            "fail",
            "N/A")

    @test.attr(type="gate")
    def test_diags_sysfsutils_package_installed_with_no_min_version_check(
            self):
        ''' Test cinder diagnostic cli tool check software command for sysfsutils package with no defined value for its version '''

        command_arvgs = [
            'software-check',
            '-software',
            "sysfsutils",
            '-service',
            'nova',
            '-test']
        ssh_mocked_response = {
            'cat /etc/*release': 'ID_LIKE=debian',
            'sysfsutils': "install ok installed 1.0 "}
        # Excecutes the check software command that needs to be tested and
        # evaluates the output
        self._check_software_package(
            'sysfsutils',
            command_arvgs,
            ssh_mocked_response,
            "pass",
            "N/A")

    @test.attr(type="gate")
    def test_diags_sg3_utils_package_installed_with_supported_version(self):
        ''' Test cinder diagnostic cli tool check software command for sg3utils package with supported version '''

        command_arvgs = [
            'software-check',
            '-software',
            "sg3-utils",
            '--package-min-version',
            '1.3',
            '-service',
            'nova',
            '-test']
        ssh_mocked_response = {
            'cat /etc/*release': 'ID_LIKE=debian',
            'sg3-utils': "install ok installed 2.2.0"}
        # Excecutes the check software command that needs to be tested and
        # evaluates the output
        self._check_software_package(
            'sg3-utils', command_arvgs, ssh_mocked_response)

    @test.attr(type="gate")
    def test_diags_sg3_utils_package_installed_with_unsupported_version(self):
        ''' Test cinder diagnostic cli tool check software command for sg3sutils package with unsupported version '''

        command_arvgs = [
            'software-check',
            '-software',
            "sg3-utils",
            '--package-min-version',
            '2.0',
            '-service',
            'nova',
            '-test']
        ssh_mocked_response = {
            'cat /etc/*release': 'ID_LIKE=debian',
            'sg3-utils': "install ok installed 1.0 "}
        # Excecutes the check software command that needs to be tested and
        # evaluates the output
        self._check_software_package(
            'sg3-utils',
            command_arvgs,
            ssh_mocked_response,
            "pass",
            "fail")

    @test.attr(type="gate")
    def test_diags_sg3_utils_package_not_installed(self):
        ''' Test cinder diagnostic cli tool check software command for non-existent sg3utils package '''

        command_arvgs = [
            'software-check',
            '-software',
            "sg3-utils",
            '--package-min-version',
            '2.0',
            '-service',
            'nova',
            '-test']
        ssh_mocked_response = {
            'cat /etc/*release': 'ID_LIKE=debian',
            'dpkg-query': 'no packages found matching  sg3-utils',
            'grep sg3-utils': ""}
        # Excecutes the check software command that needs to be tested and
        # evaluates the output
        self._check_software_package(
            'sg3-utils',
            command_arvgs,
            ssh_mocked_response,
            "fail",
            "N/A")

    @test.attr(type="gate")
    def test_diags_sg3_utils_package_installed_with_no_min_version_check(self):
        ''' Test cinder diagnostic cli tool check software command for sg3utils with no defined value for its version '''

        command_arvgs = [
            'software-check',
            '-software',
            "sysfsutils",
            '-service',
            'nova',
            '-test']
        ssh_mocked_response = {
            'cat /etc/*release': 'ID_LIKE=debian',
            'sysfsutils': "install ok installed 1.0 "}
        # Excecutes the check software command that needs to be tested and
        # evaluates the output
        self._check_software_package(
            'sysfsutils',
            command_arvgs,
            ssh_mocked_response,
            "pass",
            "N/A")

    @test.attr(type="gate")
    def test_diags_hp3parclient_package_installed_with_unsupported_version(
            self):
        ''' Test cinder diagnostic cli tool check software command for hp3parclient package with unsupported version '''

        command_arvgs = [
            'software-check',
            '-software',
            "hp3parclient",
            '--package-min-version',
            '2.0',
            '-service',
            'nova',
            '-test']
        ssh_mocked_response = {
            'cat /etc/*release': 'ID_LIKE=debian',
            'dpkg-query': 'no packages found matching  hp3parclient',
            'grep hp3parclient': "hp3parclient (1.2.2) "}
        # Excecutes the check software command that needs to be tested and
        # evaluates the output
        self._check_software_package(
            'hp3parclient',
            command_arvgs,
            ssh_mocked_response,
            "pass",
            "fail")

    @test.attr(type="gate")
    def test_diags_hp3parclients_package_not_installed(self):
        ''' Test cinder diagnostic cli tool check software command for non-existent hp3parclient package '''

        command_arvgs = [
            'software-check',
            '-software',
            "hp3parclient",
            '--package-min-version',
            '2.0',
            '-service',
            'nova',
            '-test']
        ssh_mocked_response = {
            'cat /etc/*release': 'ID_LIKE=debian',
            'dpkg-query': 'no packages found matching  hp3parclient',
            'grep hp3parclient': ""}
        # Excecutes the check software command that needs to be tested and
        # evaluates the output
        self._check_software_package(
            'hp3parclient',
            command_arvgs,
            ssh_mocked_response,
            "fail",
            "N/A")

    @test.attr(type="gate")
    def test_diags_hp3parclients_package_installed_with_no_min_version_check(
            self):
        ''' Test cinder diagnostic cli tool check software command for
            hp3parclient package with no defined value for its version
        '''

        command_arvgs = [
            'software-check',
            '-software',
            "hp3parclient",
            '-service',
            'cinder',
            '-test']
        ssh_mocked_response = {
            'cat /etc/*release': 'ID_LIKE=debian',
            'dpkg-query': 'no packages found matching  hp3parclient',
            'grep hp3parclient': "hp3parclient (3.2.2) "}
        # Excecutes the check software command that needs to be tested and
        # evaluates the output
        self._check_software_package(
            'hp3parclient',
            command_arvgs,
            ssh_mocked_response,
            "pass",
            "N/A")

    @test.attr(type="gate")
    def test_diags_check_error_with_specific_package_and_missing_service(self):
        """Test cinder diagnostic cli tool check software command for
           specific package and missing service"""

        command = 'cinderdiags software-check -name vim'
        output, return_code = self._exec_shell_command(command)
        output_len = len(output)
        self.assertEqual('cinderdiags software-check: error: unrecognized\
 arguments: -name vim', output[output_len - 1].strip())
        self.assertEqual(2, return_code)

    @test.attr(type="gate")
    def test_diags_check_error_with_specific_service_and_missing_pacakage(
            self):
        """Test cinder diagnostic cli tool check software command for
           specific service and missing pacakage"""

        command = 'cinderdiags software-check --service nova'
        output, return_code = self._exec_shell_command(command)
        output_len = len(output)
        self.assertEqual('cinderdiags software-check: error: unrecognized\
 arguments: --service nova', output[output_len - 1].strip())
        self.assertEqual(2, return_code)

    @test.attr(type="gate")
    def test_diags_check_error_with_missing_pacakage_and_service(self):
        """Test cinder diagnostic cli tool check software command for
           specific minimum version and missing pacakage and service"""

        command = 'cinderdiags software-check -package-min-version 0'
        output, return_code = self._exec_shell_command(command)
        output_len = len(output)
        self.assertEqual('cinderdiags software-check: error: unrecognized\
 arguments: -package-min-version 0', output[output_len - 1].strip())
        self.assertEqual(2, return_code)

    @test.attr(type="gate")
    def test_diags_cli_check_array_command_with_cinder_file_not_found(self):
        ''' Test cinder diagnostic cli tool check array command for non-existent cinder.conf file '''

        # Mock permiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file, True)

        # Execute the CLI commnad
        command_arvgs = ['options-check', "-test"]
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(1, cli_exit_value)
        self.assertEqual(len(output), 0)

    @test.attr(type="gate")
    def test_diags_cli_tool_with_no_cli_config(self):
        ''' Test cinder diagnostic cli tool command execution with non-existent cli.conf file '''

        # remove cli config
        self._remove_file( constant.CLI_CONFIG)
        # Execute the CLI commnad
        command_arvgs = ['options-check', "-test"]
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(1, cli_exit_value)
        self.assertEqual(len(output), 0)


    @test.attr(type="gate")
    def test_diags_cli_check_array_command_with_wrong_cinder_node_ssh_credentials(
            self):
        ''' Test cinder diagnostic cli tool check array command when wrong SSH credentials are given for cinder node '''

        # dict is the key value pair of the command and its response response
        c_mock, aa_mock, client_mock = self._set_ssh_connection_mocks()
        s_mock = self._patch('time.sleep')
        c_mock.return_value = client_mock
        client_mock.connect.side_effect = paramiko.ssh_exception.AuthenticationException()

        # Execute the CLI commnad
        command_arvgs = ['options-check', "-test"]
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(1, cli_exit_value)
        self.assertEqual(len(output), 0)

    @test.attr(type="gate")
    def test_diags_cli_ssh_timeout_while_connecting(self):
        ''' Test cinder diagnostic cli tool for SSH connection timeout with hp3parclient '''

        # dict is the key value pair of the command and its response response
        c_mock, aa_mock, client_mock = self._set_ssh_connection_mocks()
        s_mock = self._patch('time.sleep')
        c_mock.return_value = client_mock
        client_mock.connect.side_effect = socket.timeout(
            "Socket Connection Time Out")

        # Execute the CLI commnad
        command_arvgs = ['options-check', "-test"]
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(1, cli_exit_value)
        self.assertEqual(len(output), 0)

    @test.attr(type="gate")
    def test_diags_cli_tool_with_ssh_connection_fails(self):
        ''' Test cinder diagnostic cli tool for unsuccessful SSH connection with hp3parclient '''
        # remove cli config

        # dict is the key value pair of the command and its response response
        c_mock, aa_mock, client_mock = self._set_ssh_connection_mocks()
        s_mock = self._patch('time.sleep')
        c_mock.return_value = client_mock
        client_mock.exec_command.side_effect = paramiko.ssh_exception.SSHException(
            "Failed to execute the command")

        # Execute the CLI commnad
        command_arvgs = ['options-check', "-test"]
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(1, cli_exit_value)
        self.assertEqual(len(output), 0)

    @test.attr(type="gate")
    def test_diags_cli_tool_with_ssh_timeout_while_executing_command(self):
        ''' Test ssh connection timeout for the execution of cinder diagnostic cli tool command '''
        # remove cli config

        # dict is the key value pair of the command and its response response
        c_mock, aa_mock, client_mock = self._set_ssh_connection_mocks()
        s_mock = self._patch('time.sleep')
        c_mock.return_value = client_mock

        def timeout(*args, **kwargs):
            raise socket.timeout("Socket Connection Time Out")
        client_mock.exec_command.side_effect = timeout
        # Execute the CLI commnad
        command_arvgs = ['options-check', "-test"]
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(1, cli_exit_value)
        self.assertEqual(len(output), 0)

    @test.attr(type="gate")
    def test_diags_cli_tool_wrong_command(self):
        ''' Test wrong command execution for cinder diagnostic cli tool '''
        # remove cli config
        # Execute the CLI commnad
        cli_exit_value = -1
        try:
            command_arvgs = ['options-check', "--wrong", "-test"]
            cli_exit_value, output = self._execute_cli_command(command_arvgs)
            self.fail()
        except:
            self.assertEqual(-1, cli_exit_value)

    @test.attr(type="gate")
    def test_successful_ssh_connection_with_mock(self):
        ''' Test SSH Connection with mock '''

        command = 'echo hello'
        response = 'hello'
        self._mock_exec_command({command: response})

        client = None
        try:
            client = Client('127.0.0.1', 'mock', 'mock')
            output = client.execute(command)
            self.assertEqual(response, output)
        except Exception as e:
            self.fail(e.message)

        finally:
            if client is not None:
                client.disconnect()

    @test.attr(type="gate")
    def test_failed_ssh_connection_with_mock(self):
        ''' Test SSH Connection with mock '''

        command = 'echo hello'
        response = Exception("Connection unSuccessful")
        self._mock_exec_command({command: response})

        client = None
        try:
            client = Client('127.0.0.1', 'mock', 'mock')
            output = client.execute('echo Successful')
            self.fail("Connection unSuccessful")
        except Exception as e:
            self.assertEqual("Connection unSuccessful", e.message)

        finally:
            if client is not None:
                client.disconnect()

    '''
    @test.attr(type="gate")
    def test_installed_nova_pkgs(self) :
        """ Test SSH Connection with mock """
        self._mock_exec_command({"dpkg-query -W -f='${Status} ${Version}' sysfsutils" :'install ok installed 2.1.0+repack-3' ,
                                 "dpkg-query -W -f='${Status} ${Version}' sg3-utils" :'install ok installed 2.1.0+repack-3'
                                 })

        responses = pkg_checks.nova_check('127.0.0.1' , 'mock', 'mock')
        for response_item in responses :
            self.assertEqual("pass",response_item.get("installed"))
            self.assertEqual("pass",response_item.get("version"))


    @test.attr(type="gate")
    def test_uninstalled_nova_pkgs(self) :
        """ Test SSH Connection with mock """
        self._mock_exec_command({"dpkg-query -W -f='${Status} ${Version}' sysfsutils" :'dpkg-query: no packages found matching sysutils' ,
                                 "dpkg-query -W -f='${Status} ${Version}' sg3-utils" :'dpkg-query: no packages found matching sg3-utils'
                                 })
        responses = pkg_checks.nova_check('127.0.0.1' , 'fake', 'fake')
        for response_item in responses :
            self.assertEqual("fail",response_item.get("installed"))

    @test.attr(type="gate")
    def test_less_min_version_for_installed_nova_pkg(self) :
        """ Test SSH Connection with mock """

        self._mock_exec_command({"dpkg-query -W -f='${Status} ${Version}' sysfsutils" :'install ok installed 2.0+repack-3' ,
                                 "dpkg-query -W -f='${Status} ${Version}' sg3-utils" :'install ok installed 1.0+repack-3'
                                 })

        responses = pkg_checks.nova_check('127.0.0.1' , 'mock', 'mock')
        for response_item in responses :
                 self.assertEqual("fail",response_item.get("version"))

    @test.attr(type="gate")
    def test_empty_response_for_installed_nova_pkg(self) :
        """ Test SSH Connection with mock """
        self._mock_exec_command({"dpkg-query -W -f='${Status} ${Version}' sysfsutils" :'' ,
                                 "dpkg-query -W -f='${Status} ${Version}' sg3-utils" :''
                                 })

        responses = pkg_checks.nova_check('127.0.0.1' , 'mock', 'mock')
        for response_item in responses :
                 self.assertEqual("fail",response_item.get("installed"))
                 self.assertEqual(None,response_item.get("version"))

    '''

    def _check_software_package(
            self,
            package,
            command_arvgs,
            ssh_mocked_response,
            installed="pass",
            min_version="pass"):
        '''
        :param package: Name of the package that needs to be checked in the command
        :param command_arvgs: This includes command arguments
        :param ssh_mocked_response: This is a dictionary which includes its value as mocked response of the cli command to be executed
        :param installed: This includes the expected output value of the cli command for the row "Installed"
        :param  min_version: This includes the expected output value of the cli command for the row "Version"
        :return:
        '''

        # Mock paramiko ssh client to return cinder file we want
        self._mock_exec_command(ssh_mocked_response)
        # Execute the CLI commnad
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0, cli_exit_value)
        self.assertEqual(len(output), 1)

        for row in output:
            self.assertEqual(package, row['Software'])
            self.assertEqual(installed, row['Installed'])
            self.assertEqual(min_version, row['Version'])

    def _execute_cli_command(self, command_arvgs, isJson=False):
        '''
        :param command_arvgs:  This includes command arguments
        :param isJson:  If true then execute command to get JSON output from CLI and if false then default table output
        :return: cli command exit value and command output
        '''
        # To verify the CLI Table output we convert it into JSON using external
        # API and return it

        # open a file to capture the CLI output
        output_file = self._get_file_name()

        if isJson:
            # add command line arugment to get the Json output
            command_arvgs.append('-f')
            command_arvgs.append('json')

        try:
          # execute the command
            cli_exit_value = -1
            temp_store = sys.stdout
            sys.stdout = open(output_file, 'w')
            try:
                sys.argv = command_arvgs
                cli_exit_value = cli.main(sys.argv)
            except Exception:
                pass
            finally:
                sys.stdout.close()
                sys.stdout = temp_store

            data = open(output_file).read()

            if isJson:
                return cli_exit_value, json.loads(data)
            else:
                return cli_exit_value, table_output_parser.listing(data)

        finally:
            self._remove_file(output_file)

    def _exec_shell_command(self, cmd):
        """
        :param cmd: This includes command as an argument and execute it on the
        terminal
        :return: Error message and error code after executing a command on the
        terminal
        """
        try:
            proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, shell=True)
            proc.wait()
        except Exception:
            pass
        finally:
            return_code = proc.returncode
            output = proc.stdout.readlines()
            if output != []:
                line = output
            else:
                line = proc.stderr.readlines()
        return line, return_code

    def _get_file_name(self):
        '''
        This generates the name starting with output
        :return: Generated name starting with output
        '''
        return "output.%.7f.txt" % time.time()

    def _remove_file(self, file):
        '''
        :param file: Name of the file that needs to be removed
        :return:
        '''
        # remove the file
        if os.path.isfile(file) is True:
            os.remove(file)

    def _set_ssh_connection_mocks(self):
        '''
        This creates magic mock object and mock the paramiko sshclient and autoaddpolicy
        :return: Mocked instance of paramiko sshclient, Mocked instance of paramiko autoaddpolicy and magic mock object
        '''

        client_mock = mock.MagicMock()
        client_mock.connect.return_value = True

        return (self._patch('paramiko.SSHClient'),
                self._patch('paramiko.AutoAddPolicy'),
                client_mock)

    def _mock_ssh_connection(self, raiseException='None'):
        c_mock, aa_mock, client_mock = self._set_ssh_connection_mocks()
        s_mock = self._patch('time.sleep')
        if raiseException == 'None':
            c_mock.return_value = client_mock
        else:
            c_mock.return_value = raiseException

    def _mock_get_file(self, config_file, raiseException=False):
        '''
        :param config_file: Name of the cinder configuration file that needs to be copied
        :param raiseException: If true raises exception for not finding the cinder configuration file
        :return:
        '''

        c_mock, aa_mock, client_mock = self._set_ssh_connection_mocks()
        s_mock = self._patch('time.sleep')
        c_mock.return_value = client_mock
        self._mock_get_config_file(config_file, client_mock, raiseException)

    def _mock_get_config_file(
            self,
            config_file,
            client_mock,
            raiseException=False):
        '''
        :param config_file: onfig_file: Name of the cinder configuration file that needs to be copied
        :param client_mock: This client mocked object
        :param raiseException: If true raises exception for not finding the cinder configuration file
        :return:
        '''

        client_mock.open_sftp.return_value = client_mock

        def my_side_effect(*args, **kwargs):
            #fromLocation =  args[0]
            if raiseException:
                raise Exception()
            toLocation = args[1]
            shutil.copy(config_file, toLocation)

        client_mock.get.side_effect = my_side_effect

    def _mock_exec_command(self, dict, config_file=None):
        '''
        :param dict: This include key value pair for the command and respons
        :param config_file : If config_file is not None then mock get file functions too
        :return:
        '''

        c_mock, aa_mock, client_mock = self._set_ssh_connection_mocks()
        s_mock = self._patch('time.sleep')
        c_mock.return_value = client_mock
        error_mock = mock.MagicMock()
        stdout_mock = mock.MagicMock()
        stdin_mock = mock.MagicMock()

        if config_file is not None:
            self._mock_get_config_file(config_file, client_mock)

        def my_side_effect(*args, **kwargs):
            is_command_found = False
            command = args[0]

            error_mock.return_value = ""
            for key in dict.keys():
                if command != "" and key in command:
                    # Assgin return value to command
                    client_mock.readlines.return_value = dict.get(key)
                    is_command_found = True
            if not is_command_found:
                client_mock.readlines.return_value = 'command not found'

            return [stdin_mock, client_mock, error_mock]
        client_mock.exec_command.side_effect = my_side_effect

    def _patch(self, target, **kwargs):
        '''
        :param target: instance that needs to be mocked
        :param kwargs:
        :return: Mocked instance
        '''
        p = mock.patch(target, **kwargs)
        m = p.start()
        self.mock_instances.append(p)
        return m

    def _get_default_3par_iscsi_cinder_conf_section(self):
        '''
         this is default 3par ISCSI configuration section of cinder config  file .
         This require to create the test version of cinder config
        :return:
        '''

        section_name = '3PAR-SLEEPYKITTY'
        dict = {
            'volume_driver': 'cinder.volume.drivers.san.hp.hp_3par_iscsi.HP3PARISCSIDriver',
            'volume_backend_name': '3PAR-SLEEPYKITTY',
            'num_volume_device_scan_tries': 10,
            'hp3par_api_url': 'http://test.ws.url:8080/api/v1',
            'hp3par_username': 'testuser',
            'hp3par_password': 'testpass',
            'hp3par_debug': True,
            'san_ip': 'http://test.ws.url:8080/api/v1',
            'san_login': 'testuser',
            'san_password': 'testpass',
            'hp3par_cpg': 'testCPG',
            'hp3par_iscsi_ips': '1.1.1.1:3260',
            'hp3par_iscsi_chap_enabled': 'false'}
        return section_name, dict

    def _get_default_3par_fc_cinder_conf_section(self):
        '''
         this is default 3par FC configuration section of cinder config  file .
         This require to create the test version of cinder config
        :return:
        '''

        section_name = '3PAR-SLEEPYKITTY-FC'
        dict = {
            'volume_driver': 'cinder.volume.drivers.san.hp.hp_3par_fc.HP3PARFCDriver',
            'volume_backend_name': '3PAR-SLEEPYKITTY-FC',
            'hp3par_api_url': 'http://test.ws.url:8080/api/v1',
            'hp3par_username': 'testuser',
            'hp3par_password': 'testpass',
            'hp3par_debug': True,
            'san_ip': 'http://test.ws.url:8080/api/v1',
            'san_login': 'testuser',
            'san_password': 'testpass',
            'hp3par_cpg': 'testCPG'}

        return section_name, dict

    def _get_default_cli_conf_section(self, node_name):
        '''
         This is the default configuration for test version of cli.conf
        :return:
        '''

        dict = {'service': node_name,
                'host_ip': '192.168.10.5',
                'ssh_user': 'fake',
                'ssh_password': 'fake',
                'conf_source': '/etc/cinder/cinder.conf'
                }

        return dict

    def _create_config(self, config_filename, dict):
        '''
        :param config_filename: Name of file to create
        :param dict: This incldue configuration section that will be written in the given file
        :return:
        '''

        try:
            config = parser = configparser.ConfigParser()

            for section in dict.keys():
                config.add_section(section)
                section_attributs = dict.get(section)
                for key in section_attributs.keys():
                    config.set(section, key, section_attributs.get(key))
            with open(config_filename, 'w') as configfile:
                config.write(configfile)

        except Exception as e:
            raise e

#  (c) Copyright 2015 Hewlett Packard Enterprise Development LP
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from base import BaseCinderDiagnosticsCliToolTest
from cinderdiags.ssh_client import Client
import cinderdiags.pkg_checks as pkg_checks
import cinderdiags.constant as constant
import unittest
import socket
import paramiko


class CinderDiagnostics3PARCliToolTest(BaseCinderDiagnosticsCliToolTest):

    """Test case class for all 3PAR cinder Diagnostics CLI Tool."""

    cinder_config_file = "cinder.conf"

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

    def test_diags_cli_check_array_command(self):
        """Test cinder diagnostic cli tool check array command when all the
        configuration values of 3par array are correct in cinde.conf."""

        # Mock paramiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file)

        # Create cinder config file and add 3par ISCSI section
        cinder_dict = {}
        # 3par ISCSI section
        section_name, values = \
            self._get_default_3par_iscsi_cinder_conf_section()
        cinder_dict[section_name] = values

        # 3par FC section
        section_name1, valuess = \
            self._get_default_3par_fc_cinder_conf_section()
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

    def test_check_array_command_for_specific_array_name(self):
        """Test cinder diagnostic cli tool check array command for specific
        array name."""

        self._mock_get_file(self.cinder_config_file)
        cinder_dict = {}
        # 3par ISCSI section
        section_name, values = \
            self._get_default_3par_iscsi_cinder_conf_section()
        cinder_dict[section_name] = values

        # 3par FC section
        section_name1, valuess = \
            self._get_default_3par_fc_cinder_conf_section()
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
        """Test cinder diagnostic cli tool check array command when wrong array
        name is given in the command."""

        self._mock_get_file(self.cinder_config_file)
        # Create cinder config file and add 3par ISCSI section
        cinder_dict = {}
        # 3par ISCSI section
        section_name, values = \
            self._get_default_3par_iscsi_cinder_conf_section()
        cinder_dict[section_name] = values

        # 3par FC section
        section_name1, valuess = \
            self._get_default_3par_fc_cinder_conf_section()
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

    def test_diags_cli_check_array_command_for_bad_ws_api(self):
        """Test cinder diagnostic cli tool check array command when the ws api
        value of 3par array in cinder.conf is wrong."""

        # Mock paramiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file)

        # Create cinder config file and add 3par ISCSI section
        cinder_dict = {}
        # 3par ISCSI section
        iscsi_section_name, iscsi_values = \
            self._get_default_3par_iscsi_cinder_conf_section()
        iscsi_values['hp3par_api_url'] = 'http://bad.ws.url:8080/api/v1'
        cinder_dict[iscsi_section_name] = iscsi_values

        # 3par FC section
        fc_section_name, fc_values = \
            self._get_default_3par_fc_cinder_conf_section()
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

    def test_diags_cli_check_array_command_for_wrong_credential(self):
        """Test cinder diagnostic cli tool check array command when the
        credentials of 3par array in cinder.conf is wrong."""

        # Mock paramiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file)

        # Create cinder config file and add 3par ISCSI section
        cinder_dict = {}
        # 3par ISCSI section
        iscsi_section_name, iscsi_values = \
            self._get_default_3par_iscsi_cinder_conf_section()
        cinder_dict[iscsi_section_name] = iscsi_values

        # 3par FC section
        fc_section_name, fc_values = \
            self._get_default_3par_fc_cinder_conf_section()
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

    def test_diags_cli_check_array_command_for_bad_CPG(self):
        """Test cinder diagnostic cli tool check array command when the cpg
        value of 3par array in cinder.conf is wrong."""

        # Mock paramiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file)

        # Create cinder config file and add 3par ISCSI section
        cinder_dict = {}
        # 3par ISCSI section
        iscsi_section_name, iscsi_values = \
            self._get_default_3par_iscsi_cinder_conf_section()
        iscsi_values['hp3par_cpg'] = 'badCPG'
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

    def test_diags_cli_check_array_command_for_one_bad_CPG(self):
        """Test cinder diagnostic cli tool check array command when the cpg
        value of 3par array in cinder.conf is wrong."""

        # Mock paramiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file)

        # Create cinder config file and add 3par ISCSI section
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

    def test_diags_cli_check_array_command_for_wrong_iscsi_IP(self):
        """Test cinder diagnostic cli tool check array command when the ISCSI
        IP of 3par array in cinder.conf is wrong."""

        # Mock paramiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file)

        # Create cinder config file and add 3par ISCSI section
        cinder_dict = {}
        # 3par ISCSI section
        iscsi_section_name, iscsi_values = \
            self._get_default_3par_iscsi_cinder_conf_section()

        iscsi_values['hp3par_iscsi_ips'] = '10.20.15.11:3260'
        cinder_dict[iscsi_section_name] = iscsi_values

        # 3par FC section
        fc_section_name, fc_values = \
            self._get_default_3par_fc_cinder_conf_section()
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

    def test_diags_cli_check_array_command_for_wrong_hp3pardriver(self):
        """Test cinder diagnostic cli tool check array command when the volume
        driver value of 3par array in cinder.conf is wrong."""

        self._mock_exec_command({'locate': None})
        # Mock paramiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file)

        # Create cinder config file and add 3par ISCSI section
        cinder_dict = {}
        # 3par ISCSI section
        iscsi_section_name, iscsi_values = \
            self._get_default_3par_iscsi_cinder_conf_section()

        iscsi_values['volume_driver'] = 'cinder.volume.drivers.san.hp.\
        hp_3par_iscsi.HP3PARWrongDriver'
        cinder_dict[iscsi_section_name] = iscsi_values

        # 3par FC section
        fc_section_name, fc_values = \
            self._get_default_3par_fc_cinder_conf_section()
        fc_values['volume_driver'] = 'cinder.volume.drivers.san.hp.\
        hp_3par_fc.HP3PARWrongDriver'
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

    def test_diags_cli_check_array_command_for_wrong_hp3pardriver(self):
        """Test cinder diagnostic cli tool check array command when the volume
        driver value of 3par array in cinder.conf is correct."""

        self._mock_exec_command(
            {
                'locate hp_3par_iscsi': '/opt/stack/cinder/cinder/volume\
                /drivers/san/hp/hp_3par_iscsi.py',
                'locate hp_3par_fc': '/opt/stack/cinder/cinder/volume\
                /drivers/san/hp/hp_3par_fc.py'},
            self.cinder_config_file)

        # Create cinder config file and add 3par ISCSI section
        cinder_dict = {}
        # 3par ISCSI section
        iscsi_section_name, iscsi_values = \
            self._get_default_3par_iscsi_cinder_conf_section()
        cinder_dict[iscsi_section_name] = iscsi_values

        # 3par FC section
        fc_section_name, fc_values = \
            self._get_default_3par_fc_cinder_conf_section()
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

    def test_diags_all_packages_installed_with_supported_version_on_ubuntu(
            self):
        """Test cinder diagnostic cli tool check software command for all the
        packages with supported version on ubuntu operating system."""

        command_arvgs = ['software-check', '-test']

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

    def test_diags_all_packages_installed_with_supported_version_on_suse(
            self):
        """Test cinder diagnostic cli tool check software command for all the
        packages with supported version SUSE operating system."""

        command_arvgs = ['software-check', '-test']

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

    def test_diags_all_packages_not_installed_with_supported_version_on_suse(
            self):
        """Test cinder diagnostic cli tool check software command for all the
        packages with supported version SUSE operating system."""

        command_arvgs = ['software-check', '-test']

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

    def test_diags_all_packages_installed_with_not_supported_version_on_suse(
            self):
        """Test cinder diagnostic cli tool check software command for all the
        packages with supported version SUSE operating system."""

        command_arvgs = ['software-check', '-test']

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

    def test_diags_all_packages_installed_with_supported_version_on_centos(
            self):
        """Test cinder diagnostic cli tool check software command for all the
        packages with supported version centos operating system."""

        command_arvgs = ['software-check', '-test']

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

    def test_diags_all_packages_not_installed_with_supported_version_on_centos(
            self):
        """Test cinder diagnostic cli tool check software command for all the
        packages with supported version centos operating system."""

        command_arvgs = ['software-check', '-test']

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

    def test_diags_all_packages_installed_with_unsupported_version_on_centos(
            self):
        """Test cinder diagnostic cli tool check software command for all the
        packages with supported version centos operating system."""

        command_arvgs = ['software-check', '-test']

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

    def test_diags_sysfsutils_package_installed_with_supported_version(self):
        """Test cinder diagnostic cli tool check software command for
        sysfsutils package with supported version."""

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

    def test_diags_sysfsutils_package_installed_with_unsupported_version(self):
        """Test cinder diagnostic cli tool check software command for
        sysfsutils package with unsupported version."""

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

    def test_diags_sysfsutils_package_not_installed(self):
        """Test cinder diagnostic cli tool check software command for
        non-existent sysfsutils package."""

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

    def test_diags_sysfsutils_package_installed_with_no_min_version_check(
            self):
        """Test cinder diagnostic cli tool check software command for
        sysfsutils package with no defined value for its version."""

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

    def test_diags_sg3_utils_package_installed_with_supported_version(self):
        """Test cinder diagnostic cli tool check software command for sg3utils
        package with supported version."""

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

    def test_diags_sg3_utils_package_installed_with_unsupported_version(self):
        """Test cinder diagnostic cli tool check software command for sg3sutils
        package with unsupported version."""

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

    def test_diags_sg3_utils_package_not_installed(self):
        """Test cinder diagnostic cli tool check software command for
        non-existent sg3utils package."""

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

    def test_diags_sg3_utils_package_installed_with_no_min_version_check(self):
        """Test cinder diagnostic cli tool check software command for sg3utils
        with no defined value for its version."""

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

    def test_diags_hp3parclient_package_installed_with_unsupported_version(
            self):
        """Test cinder diagnostic cli tool check software command for
        hp3parclient package with unsupported version."""

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

    def test_diags_hp3parclients_package_not_installed(self):
        """Test cinder diagnostic cli tool check software command for
        non-existent hp3parclient package."""

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

    def test_diags_hp3parclients_package_installed_with_no_min_version_check(
            self):
        """Test cinder diagnostic cli tool check software command for
        hp3parclient package with no defined value for its version."""

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

    def test_diags_check_error_with_specific_package_and_missing_service(self):
        """Test cinder diagnostic cli tool check software command for specific
        package and missing service."""

        command = 'cinderdiags software-check -name vim'
        output, return_code = self._exec_shell_command(command)
        output_len = len(output)
        self.assertEqual(b'cinderdiags software-check: error: unrecognized\
 arguments: -name vim', output[output_len - 1].strip())
        self.assertEqual(2, return_code)

    def test_diags_check_error_with_specific_service_and_missing_pacakage(
            self):
        """Test cinder diagnostic cli tool check software command for specific
        service and missing pacakage."""

        command = 'cinderdiags software-check --service nova'
        output, return_code = self._exec_shell_command(command)
        output_len = len(output)
        self.assertEqual(b'cinderdiags software-check: error: unrecognized\
 arguments: --service nova', output[output_len - 1].strip())
        self.assertEqual(2, return_code)

    def test_diags_check_error_with_missing_pacakage_and_service(self):
        """Test cinder diagnostic cli tool check software command for specific
        minimum version and missing pacakage and service."""

        command = 'cinderdiags software-check -package-min-version 0'
        output, return_code = self._exec_shell_command(command)
        output_len = len(output)
        self.assertEqual(b'cinderdiags software-check: error: unrecognized\
 arguments: -package-min-version 0', output[output_len - 1].strip())
        self.assertEqual(2, return_code)

    @test.attr(type="gate")
    def test_diags_check_cinderdiags_help_call(self):
        """Test cinder diagnostic cli tool help call."""

        command = 'cinderdiags -h'
        output, return_code = self._exec_shell_command(command)
        optional_arguments = output.index('optional arguments:\n')
        commands = output.index('Commands:\n')
        self.assertEqual('optional arguments:',
                         output[optional_arguments].strip())
        self.assertEqual('Commands:', output[commands].strip())
        self.assertEqual(0, return_code)

    @test.attr(type="gate")
    def test_diags_check_array_command_help_call(self):
        """Test cinder diagnostic cli tool help call for check array
        command."""

        command = 'cinderdiags --help options-check'
        output, return_code = self._exec_shell_command(command)
        output_data = output.index('output data:\n')
        optional_arguments = output.index('optional arguments:\n')
        output_formatters = output.index('output formatters:\n')
        table_formatter = output.index('table formatter:\n')
        CSV_Formatter = output.index('CSV Formatter:\n')
        self.assertEqual('output data:', output[output_data].strip())
        self.assertEqual('optional arguments:',
                         output[optional_arguments].strip())
        self.assertEqual('output formatters:',
                         output[output_formatters].strip())
        self.assertEqual('table formatter:', output[table_formatter].strip())
        self.assertEqual('CSV Formatter:', output[CSV_Formatter].strip())
        self.assertEqual(0, return_code)

    @test.attr(type="gate")
    def test_diags_check_software_command_help_call(self):
        """Test cinder diagnostic cli tool help call for check software
        command."""

        command = 'cinderdiags -h software-check'
        output, return_code = self._exec_shell_command(command)
        output_data = output.index('output data:\n')
        optional_arguments = output.index('optional arguments:\n')
        output_formatters = output.index('output formatters:\n')
        table_formatter = output.index('table formatter:\n')
        CSV_Formatter = output.index('CSV Formatter:\n')
        self.assertEqual('output data:', output[output_data].strip())
        self.assertEqual('optional arguments:',
                         output[optional_arguments].strip())
        self.assertEqual('output formatters:',
                         output[output_formatters].strip())
        self.assertEqual('table formatter:', output[table_formatter].strip())
        self.assertEqual('CSV Formatter:', output[CSV_Formatter].strip())
        self.assertEqual(0, return_code)

    def test_diags_cli_check_array_command_with_cinder_file_not_found(self):
        """Test cinder diagnostic cli tool check array command for
        non-existent cinder.conf file."""

        # Mock permiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file, True)

        # Execute the CLI commnad
        command_arvgs = ['options-check', "-test"]
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(1, cli_exit_value)
        self.assertEqual(len(output), 0)

    def test_diags_cli_tool_with_no_cli_config(self):
        """Test cinder diagnostic cli tool command execution with non-existent
        cli.conf file."""

        # Remove cli config
        self._remove_file(constant.CLI_CONFIG)
        # Execute the CLI commnad
        command_arvgs = ['options-check', "-test"]
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(1, cli_exit_value)
        self.assertEqual(len(output), 0)

    def test_diags_check_array_command_with_wrong_cinder_node_ssh_credentials(
            self):
        """Test cinder diagnostic cli tool check array command when wrong SSH
        credentials are given for cinder node."""

        c_mock, aa_mock, client_mock = self._set_ssh_connection_mocks()
        s_mock = self._patch('time.sleep')
        c_mock.return_value = client_mock
        client_mock.connect.side_effect = paramiko.ssh_exception.\
            AuthenticationException()

        # Execute the CLI commnad
        command_arvgs = ['options-check', "-test"]
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(1, cli_exit_value)
        self.assertEqual(len(output), 0)

    def test_diags_cli_ssh_timeout_while_connecting(self):
        """Test cinder diagnostic cli tool for SSH connection timeout with
        hp3parclient."""

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

    def test_diags_cli_tool_with_ssh_connection_fails(self):
        """Test cinder diagnostic cli tool for unsuccessful SSH connection with
        hp3parclient."""

        c_mock, aa_mock, client_mock = self._set_ssh_connection_mocks()
        s_mock = self._patch('time.sleep')
        c_mock.return_value = client_mock
        client_mock.exec_command.side_effect = paramiko.ssh_exception.\
            SSHException("Failed to execute the command")

        # Execute the CLI commnad
        command_arvgs = ['options-check', "-test"]
        cli_exit_value, output = self._execute_cli_command(command_arvgs)

        self.assertEqual(1, cli_exit_value)
        self.assertEqual(len(output), 0)

    def test_diags_cli_tool_with_ssh_timeout_while_executing_command(self):
        """Test ssh connection timeout for the execution of cinder diagnostic
        cli tool command."""

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

    def test_diags_cli_tool_wrong_command(self):
        """Test wrong command execution for cinder diagnostic cli tool."""

        # Execute the CLI commnad
        cli_exit_value = -1
        try:
            command_arvgs = ['options-check', "--wrong", "-test"]
            cli_exit_value, output = self._execute_cli_command(command_arvgs)
            self.fail()
        except:
            self.assertEqual(-1, cli_exit_value)

    def test_successful_ssh_connection_with_mock(self):
        """Test successful SSH Connection with mock."""

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

    def test_failed_ssh_connection_with_mock(self):
        """Test unsuccessful SSH Connection with mock."""

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

suite = unittest.TestLoader().loadTestsFromTestCase(
    CinderDiagnostics3PARCliToolTest)
unittest.TextTestRunner(verbosity=2).run(suite)

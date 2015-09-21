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


import unittest
import mock
import time
import subprocess
import sys
import shutil
import re
import os
import json
from six.moves import configparser
import cinderdiags.main as cli


class BaseCinderDiagnosticsCliToolTest(unittest.TestCase):

    delimiter_line = re.compile('^\+\-[\+\-]+\-\+$')

    def _check_software_package(
            self,
            package,
            command_arvgs,
            ssh_mocked_response,
            installed="pass",
            min_version="pass"):
        """
        :param package: Name of the package that needs to be checked in the
        command
        :param command_arvgs: This includes command arguments
        :param ssh_mocked_response: This is a dictionary which includes its
        value as mocked response of the cli command to be executed
        :param installed: This includes the expected output value of the cli
        command for the row "Installed"
        :param  min_version: This includes the expected output value of the cli
        command for the row "Version"
        :return:
        """

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
        """
        :param command_arvgs:  This includes command arguments
        :param isJson:  If true then execute command to get JSON output from
        CLI and if false then default table output
        :return: cli command exit value and command output
        """
        # To verify the CLI Table output we convert it into JSON using external
        # API and return it

        # Open a file to capture the CLI output
        output_file = self._get_file_name()

        if isJson:
            # Add command line arugment to get the Json output
            command_arvgs.append('-f')
            command_arvgs.append('json')

        try:
            # Execute the command
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
                return cli_exit_value, self.listing(data)

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
        """This generates the name starting with output.

        :return: Generated name starting with output
        """
        return "output.%.7f.txt" % time.time()

    def _remove_file(self, file):
        """
        :param file: Name of the file that needs to be removed
        :return:
        """
        # Remove the file
        if os.path.isfile(file) is True:
            os.remove(file)

    def _set_ssh_connection_mocks(self):
        """This creates magic mock object and mock the paramiko sshclient and
        autoaddpolicy.

        :return: Mocked instance of paramiko sshclient, Mocked instance of
        paramiko autoaddpolicy and magic mock object
        """

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
        """
        :param config_file: Name of the cinder configuration file that needs to
        be copied
        :param raiseException: If true raises exception for not finding the
        cinder configuration file
        :return:
        """

        c_mock, aa_mock, client_mock = self._set_ssh_connection_mocks()
        s_mock = self._patch('time.sleep')
        c_mock.return_value = client_mock
        self._mock_get_config_file(config_file, client_mock, raiseException)

    def _mock_get_config_file(
            self,
            config_file,
            client_mock,
            raiseException=False):
        """
        :param config_file: onfig_file: Name of the cinder configuration file
        that needs to be copied
        :param client_mock: This is client mocked object
        :param raiseException: If true raises exception for not finding the
        cinder configuration file
        :return:
        """

        client_mock.open_sftp.return_value = client_mock

        def my_side_effect(*args, **kwargs):
            # fromLocation =  args[0]
            if raiseException:
                raise Exception()
            toLocation = args[1]
            shutil.copy(config_file, toLocation)

        client_mock.get.side_effect = my_side_effect

    def _mock_exec_command(self, dict, config_file=None):
        """
        :param dict: This include key value pair for the command and response
        :param config_file : If config_file is not None then mock get file
        functions too
        :return:
        """

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
        """
        :param target: instance that needs to be mocked
        :param kwargs:
        :return: Mocked instance
        """
        p = mock.patch(target, **kwargs)
        m = p.start()
        self.mock_instances.append(p)
        return m

    def _get_default_3par_iscsi_cinder_conf_section(self):
        """This is default 3par ISCSI configuration section of cinder config
        file . This require to create the test version of cinder config.

        :return:
        """

        section_name = '3PAR-SLEEPYKITTY'
        dict = {
            'volume_driver': 'cinder.volume.drivers.san.hp.\
            hp_3par_iscsi.HP3PARISCSIDriver',
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
        """This is default 3par FC configuration section of cinder config  file
        . This require to create the test version of cinder config.

        :return:
        """

        section_name = '3PAR-SLEEPYKITTY-FC'
        dict = {
            'volume_driver': 'cinder.volume.drivers.san.hp.\
            hp_3par_fc.HP3PARFCDriver',
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
        """This is the default configuration for test version of cli.conf.

        :return:
        """

        dict = {'service': node_name,
                'host_ip': '192.168.10.5',
                'ssh_user': 'fake',
                'ssh_password': 'fake',
                'conf_source': '/etc/cinder/cinder.conf'
                }

        return dict

    def _create_config(self, config_filename, dict):
        """
        :param config_filename: Name of file to create
        :param dict: This incldue configuration section that will be written
        in the given file
        :return:
        """

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

    def table(self, output_lines):
        """Parse single table from cli output.

        Return dict with list of column names in 'headers' key and rows
        in 'values' key.
        """
        table_ = {'headers': [], 'values': []}
        columns = None

        if not isinstance(output_lines, list):
            output_lines = output_lines.split('\n')

        if not output_lines[-1]:
            # Skip last line if empty (just newline at the end)
            output_lines = output_lines[:-1]

        for line in output_lines:
            if self. delimiter_line.match(line):
                columns = self.table_columns(line)
                continue
            if '|' not in line:
                continue
            row = []
            for col in columns:
                row.append(line[col[0]:col[1]].strip())
            if table_['headers']:
                table_['values'].append(row)
            else:
                table_['headers'] = row

        return table_

    def table_columns(self, first_table_row):
        """Find column ranges in output line.

        Return list of tuples (start,end) for each column detected by
        plus (+) characters in delimiter line.
        """
        positions = []
        start = 1  # there is '+' at 0
        while start < len(first_table_row):
            end = first_table_row.find('+', start)
            if end == -1:
                break
            positions.append((start, end))
            start = end + 1
        return positions

    def listing(self, output_lines):
        """Return list of dicts with basic item info parsed from cli output."""

        items = []
        table_ = self.table(output_lines)
        for row in table_['values']:
            item = {}
            for col_idx, col_key in enumerate(table_['headers']):
                item[col_key] = row[col_idx]
            items.append(item)
        return items


import mock
import time
import ConfigParser
import os
import pkg_checks
from tempest.api.volume import base
from tempest import test
from tempest import config
from tempest_lib.cli import output_parser
from cinderdiags.ssh_client import Client

import cinderdiags.main as cli
import sys


class CinderDiagnostics3PARCliToolTest(base.BaseVolumeAdminTest):

    """Test case class for all 3PAR cinder Diagnostics CLI Tool """


    @classmethod
    def resource_setup(cls):
        super(CinderDiagnostics3PARCliToolTest, cls).resource_setup()
        cls.mock_instances = []

    @classmethod
    def resource_cleanup(cls):
        for mock_instance in cls.mock_instances :
             mock_instance.stop()

    @test.attr(type="gate")
    def test_successful_ssh_connection_with_mock(self) :
        """ Test SSH Connection with mock """

        command = 'echo hello'
        response = 'hello'
        self._mock_exec_command({command :response})

        client = None
        try :
            client = Client('127.0.0.1' , 'mock', 'mock')
            output = client.execute(command)
            self.assertEqual(response , output)
        except Exception as e :
            self.fail(e.message)

        finally:
            if client is not None :
                client.disconnect()

    @test.attr(type="gate")
    def test_failed_ssh_connection_with_mock(self) :
        """ Test SSH Connection with mock """

        command = 'echo hello'
        response = Exception("Connection unSuccessful")
        self._mock_exec_command({command :response})

        client = None
        try :
            client = Client('127.0.0.1' , 'mock', 'mock')
            output = client.execute('echo Successful')
            self.fail("Connection unSuccessful" )
        except Exception as e :
            self.assertEqual("Connection unSuccessful", e.message)

        finally:
            if client is not None :
                client.disconnect()


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


    @test.attr(type="gate")
    def test_diags_cli_check_array_command(self) :

        # Mock permiko ssh client to return cinder file we want
        self._mock_get_file("cinder.conf")

        # create cinder config,conf file and add 3par ISCSI section
        dict = { }
        # 3par ISCSI section
        section_name, values = self._get_default_3par_iscsi_cinder_conf_section()
        dict[section_name] = values

        # 3par FC section
        section_name, values = self._get_default_3par_fc_cinder_conf_section()
        dict[section_name] = values
        #Create cinder.conf
        self._create_config("cinder.conf",  dict)

        output_file  = "output.%.7f.txt" % time.time()

        #open a file to capture the CLI output
        sys.stdout  = open(output_file, 'w')

        # Execute the CLI commnad
        arv=['check', 'array']
        cli_exit_value = cli.main(arv)
        self.assertEqual(0 , cli_exit_value)

        table_output = self._convert_table_output(output_file)

        for row in table_output :
            self.assertEqual('CINDER' , row['node'])
            self.assertEqual('pass' , row['CPG'])
            self.assertEqual('pass' , row['Credentials'])
            self.assertEqual('pass' , row['WS API'])


        # remove the file
        if os.path.isfile(output_file) is True:
                os.remove(output_file)

        if os.path.isfile("cinder.conf") is True:
                os.remove("cinder.conf")

    def _convert_table_output(self, filename):

        data = open(filename).read()
        return output_parser.listing(data)


    def _set_ssh_connection_mocks(self):

        client_mock = mock.MagicMock()
        client_mock.connect.return_value = True

        return (self._patch('paramiko.SSHClient'),
                self._patch('paramiko.AutoAddPolicy'),
                client_mock)

    def _mock_get_file(self, config_file):
         c_mock, aa_mock, client_mock = self._set_ssh_connection_mocks()
         s_mock = self._patch('time.sleep')
         c_mock.return_value = client_mock

         client_mock.open_sftp.return_value = client_mock

         def my_side_effect(*args, **kwargs):
                 #fromLocation =  args[0]
                 toLocation  =  args[1]
                 os.popen("sudo cp " + config_file + " " +toLocation)


         client_mock.get.side_effect = my_side_effect

    def _mock_exec_command(self, dict):

         # dict is the key value pair of the command and its response response
         c_mock, aa_mock, client_mock = self._set_ssh_connection_mocks()
         s_mock = self._patch('time.sleep')
         c_mock.return_value = client_mock

         def my_side_effect(*args, **kwargs):
              is_command_found = False
              for key in dict.keys() :
                 if args[0] == key:
                     # Assgin return value to command
                     client_mock.read.return_value =  dict.get(key)
                     is_command_found = True
              if not is_command_found :
                   client_mock.read.return_value = 'command not found'
              return [[], client_mock]

         client_mock.exec_command.side_effect = my_side_effect



    def _patch(self, target, **kwargs):

        p = mock.patch(target, **kwargs)
        m = p.start()
        self. mock_instances.append(p)
        return m


    def _get_default_3par_iscsi_cinder_conf_section(self) :

        section_name = '3PAR-SLEEPYKITTY'
        dict = {  'volume_driver' : 'cinder.volume.drivers.san.hp.hp_3par_iscsi.HP3PARISCSIDriver',
                  'volume_backend_name' : '3PAR-SLEEPYKITTY',
                  'num_volume_device_scan_tries' : 10,
                  'hp3par_api_url' : 'https://sleepykitty.cxo.hp.com:8080/api/v1',
                  'hp3par_username' : '3paradm',
                  'hp3par_password' : '3pardata',
                  'hp3par_debug' : True,
                  'san_ip': 'sleepykitty.cxo.hp.com',
                   'san_login' : '3paradm',
                   'san_password' : '3pardata',
                   'hp3par_cpg' : 'OpenStackCPG1',
                   'hp3par_iscsi_ips' : '10.250.100.220:3260',
                   'hp3par_iscsi_chap_enabled' : 'false' }
        return section_name , dict

    def _get_default_3par_fc_cinder_conf_section(self) :

        section_name = '3PAR-SLEEPYKITTY-FC'
        dict = {  'volume_driver' : 'cinder.volume.drivers.san.hp.hp_3par_fc.HP3PARFCDriver',
                  'volume_backend_name' : '3PAR-SLEEPYKITTY-FC',
                  'hp3par_api_url' : 'https://sleepykitty.cxo.hp.com:8080/api/v1',
                  'hp3par_username' : '3paradm',
                  'hp3par_password' : '3pardata',
                  'hp3par_debug' : True,
                  'san_ip': 'sleepykitty.cxo.hp.com',
                   'san_login' : '3paradm',
                   'san_password' : '3pardata',
                   'hp3par_cpg' : 'OpenStackCPG1' }

        return section_name , dict

    def _create_config(self, config_filename, dict) :

                try :
                   config = ConfigParser.RawConfigParser(allow_no_value=True)

                   for section in dict.keys():
                       config.add_section(section)
                       section_attributs = dict.get(section)
                       for key in section_attributs.keys():
                             config.set(section,key,section_attributs.get(key))
                   with open(config_filename, 'w') as configfile:
                       config.write(configfile)

                except Exception as e :
                    raise e



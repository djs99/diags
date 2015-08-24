
import mock
import time
import ConfigParser
import os
from tempest.api.volume import base
from tempest import test
from tempest import config
from tempest_lib.cli import output_parser
from cinderdiags.ssh_client import Client
import cinderdiags.main as cli
import cinderdiags.pkg_checks as pkg_checks
import sys
import shutil
import paramiko


class CinderDiagnostics3PARCliToolTest(base.BaseVolumeAdminTest):

    """Test case class for all 3PAR cinder Diagnostics CLI Tool """

    cinder_config_file = "cinder.conf"
    
    @classmethod
    def resource_setup(cls):
        super(CinderDiagnostics3PARCliToolTest, cls).resource_setup()


        if not os.path.exists('cinderdiags')  :
               os.mkdir('cinderdiags',False)
        if not os.path.exists('config')  :
               os.mkdir('config', False)

    @classmethod
    def resource_cleanup(cls):
        if os.path.exists('cinderdiags')  :
            shutil.rmtree("cinderdiags")
        if os.path.exists('config')  :
            shutil.rmtree("config")




    @test.attr(type="gate")
    def test_diags_cli_check_array_command(self) :

        # Mock permiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file)


        # create cinder config,conf file and add 3par ISCSI section
        cinder_dict = { }
        # 3par ISCSI section
        section_name, values = self._get_default_3par_iscsi_cinder_conf_section()
        cinder_dict[section_name] = values

        # 3par FC section
        section_name1, valuess = self._get_default_3par_fc_cinder_conf_section()
        cinder_dict[section_name1] = valuess

        #Create cinder.conf
        self._create_config(self.cinder_config_file,  cinder_dict)


        # Execute the CLI commnad
        command_arvgs=['check', 'array', "-test"]
        cli_exit_value , output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0 , cli_exit_value)
        self.assertEqual(len(output) , 2)

        for row in output :
            self.assertEqual('TEST' , row['Node'])
            self.assertEqual('pass' , row['CPG'])
            self.assertEqual('pass' , row['Credentials'])
            self.assertEqual('pass' , row['WS API'])
            if row['Name'] == '3PAR-SLEEPYKITTY-FC' :
               self.assertEqual('N/A' , row['iSCSI IP(s)'])
            else :
               self.assertEqual('pass' , row['iSCSI IP(s)'])



        self._remove_file(self.cinder_config_file)




    @test.attr(type="gate")
    def test_diags_cli_check_array_command_for_bad_ws_api(self) :

        # Mock permiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file)


        # create cinder config,conf file and add 3par ISCSI section
        cinder_dict = { }
        # 3par ISCSI section
        iscsi_section_name, iscsi_values = self._get_default_3par_iscsi_cinder_conf_section()
        iscsi_values['hp3par_api_url'] = 'http://bad.ws.url:8080/api/v1'
        cinder_dict[iscsi_section_name] = iscsi_values

        # 3par FC section
        fc_section_name, fc_values = self._get_default_3par_fc_cinder_conf_section()
        cinder_dict[fc_section_name] = fc_values

        #Create cinder.conf
        self._create_config(self.cinder_config_file,  cinder_dict)


        # Execute the CLI commnad
        command_arvgs=['check', 'array', "-test"]
        cli_exit_value , output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0 , cli_exit_value)
        self.assertEqual( len(output) , 2)

        for row in output :
           if row['Name'] == iscsi_section_name :
              self.assertEqual('TEST' , row['Node'])
              self.assertEqual('unknown' , row['CPG'])
              self.assertEqual('unknown' , row['Credentials'])
              self.assertEqual('fail' , row['WS API'])
              self.assertEqual('unknown' , row['iSCSI IP(s)'])
           else :
              self.assertEqual('TEST' , row['Node'])
              self.assertEqual('pass' , row['CPG'])
              self.assertEqual('pass' , row['Credentials'])
              self.assertEqual('pass' , row['WS API'])
              self.assertEqual('N/A' , row['iSCSI IP(s)'])

        self._remove_file(self.cinder_config_file)


    @test.attr(type="gate")
    def test_diags_cli_check_array_command_for_wrong_credential(self) :
        # Mock permiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file)

        # create cinder config,conf file and add 3par ISCSI section
        cinder_dict = { }
        # 3par ISCSI section
        iscsi_section_name, iscsi_values = self._get_default_3par_iscsi_cinder_conf_section()
        cinder_dict[iscsi_section_name] = iscsi_values

        # 3par FC section
        fc_section_name, fc_values = self._get_default_3par_fc_cinder_conf_section()
        fc_values['hp3par_username'] = 'baduser'
        fc_values['hp3par_password'] = 'badpass'
        cinder_dict[fc_section_name] = fc_values

        #Create cinder.conf
        self._create_config(self.cinder_config_file,  cinder_dict)


        # Execute the CLI commnad
        command_arvgs=['check', 'array', "-test"]
        cli_exit_value , output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0 , cli_exit_value)
        self.assertEqual( len(output) , 2)

        for row in output :
           if row['Name'] == iscsi_section_name :
              self.assertEqual('TEST' , row['Node'])
              self.assertEqual('pass' , row['CPG'])
              self.assertEqual('pass' , row['Credentials'])
              self.assertEqual('pass' , row['WS API'])
              self.assertEqual('pass' , row['iSCSI IP(s)'])
           else :
              self.assertEqual('TEST' , row['Node'])
              self.assertEqual('unknown' , row['CPG'])
              self.assertEqual('fail' , row['Credentials'])
              self.assertEqual('pass' , row['WS API'])
              self.assertEqual('N/A' , row['iSCSI IP(s)'])

        self._remove_file(self.cinder_config_file)



    @test.attr(type="gate")
    def test_diags_cli_check_array_command_for_bad_CPG(self) :

       # Mock permiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file)

        # create cinder config,conf file and add 3par ISCSI section
        cinder_dict = { }
        # 3par ISCSI section
        iscsi_section_name, iscsi_values = self._get_default_3par_iscsi_cinder_conf_section()
        iscsi_values['hp3par_cpg'] = 'badCPG'
        cinder_dict[iscsi_section_name] = iscsi_values

        # 3par FC section
        fc_section_name, fc_values = self._get_default_3par_fc_cinder_conf_section()
        fc_values['hp3par_username'] = 'baduser'
        fc_values['hp3par_password'] = 'badpass'
        cinder_dict[fc_section_name] = fc_values

        #Create cinder.conf
        self._create_config(self.cinder_config_file,  cinder_dict)


        # Execute the CLI commnad
        command_arvgs=['check', 'array', "-test"]
        cli_exit_value , output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0 , cli_exit_value)
        self.assertEqual( len(output) , 2)

        for row in output :
           if row['Name'] == iscsi_section_name :
              self.assertEqual('TEST' , row['Node'])
              self.assertEqual('fail' , row['CPG'])
              self.assertEqual('pass' , row['Credentials'])
              self.assertEqual('pass' , row['WS API'])
              self.assertEqual('pass' , row['iSCSI IP(s)'])
           else :
              self.assertEqual('TEST' , row['Node'])
              self.assertEqual('unknown' , row['CPG'])
              self.assertEqual('fail' , row['Credentials'])
              self.assertEqual('pass' , row['WS API'])
              self.assertEqual('N/A' , row['iSCSI IP(s)'])

        self._remove_file(self.cinder_config_file)


    @test.attr(type="gate")
    def test_diags_cli_check_array_command_for_wrong_iscsi_IP(self) :

        # Mock permiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file)

        # create cinder config,conf file and add 3par ISCSI section
        cinder_dict = { }
        # 3par ISCSI section
        iscsi_section_name, iscsi_values = self._get_default_3par_iscsi_cinder_conf_section()

        iscsi_values['hp3par_iscsi_ips'] = '10.20.15.11:3260'
        cinder_dict[iscsi_section_name] = iscsi_values

        # 3par FC section
        fc_section_name, fc_values = self._get_default_3par_fc_cinder_conf_section()
        fc_values['hp3par_cpg'] = 'badCPG'
        cinder_dict[fc_section_name] = fc_values

        #Create cinder.conf
        self._create_config(self.cinder_config_file,  cinder_dict)


        # Execute the CLI commnad
        command_arvgs=['check', 'array', "-test"]
        cli_exit_value , output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0 , cli_exit_value)
        self.assertEqual( len(output) , 2)

        for row in output :
           if row['Name'] == iscsi_section_name :
              self.assertEqual('TEST' , row['Node'])
              self.assertEqual('pass' , row['CPG'])
              self.assertEqual('pass' , row['Credentials'])
              self.assertEqual('pass' , row['WS API'])
              self.assertEqual('fail' , row['iSCSI IP(s)'])
           else :
              self.assertEqual('TEST' , row['Node'])
              self.assertEqual('fail' , row['CPG'])
              self.assertEqual('pass' , row['Credentials'])
              self.assertEqual('pass' , row['WS API'])
              self.assertEqual('N/A' , row['iSCSI IP(s)'])

        self._remove_file(self.cinder_config_file)

    @test.attr(type="gate")
    def test_diags_cli_check_array_command_with_cinder_file_not_found(self) :

        # Mock permiko ssh client to return cinder file we want
        self._mock_get_file(self.cinder_config_file,True)

        # create cinder config,conf file and add 3par ISCSI section
        cinder_dict = { }
        # 3par ISCSI section
        iscsi_section_name, iscsi_values = self._get_default_3par_iscsi_cinder_conf_section()

        iscsi_values['hp3par_iscsi_ips'] = '10.20.15.11:3260'
        cinder_dict[iscsi_section_name] = iscsi_values

        # 3par FC section
        fc_section_name, fc_values = self._get_default_3par_fc_cinder_conf_section()
        fc_values['hp3par_cpg'] = 'badCPG'
        cinder_dict[fc_section_name] = fc_values

        #Create cinder.conf
        self._create_config(self.cinder_config_file,  cinder_dict)


        # Execute the CLI commnad
        command_arvgs=['check', 'array', "-test"]
        cli_exit_value , output = self._execute_cli_command(command_arvgs)

        self.assertEqual(1 , cli_exit_value)
        self.assertEqual( len(output) , 0)


        self._remove_file(self.cinder_config_file)

    @test.attr(type="gate")
    def test_diags_cli_check_array_command_with_wrong_cinder_node_ssh_credentials(self) :

        # Mock permiko ssh client to return cinder file we want
        self._mock_ssh_connection(paramiko.ssh_exception.AuthenticationException ())

        # create cinder config,conf file and add 3par ISCSI section
        cinder_dict = { }
        # 3par ISCSI section
        iscsi_section_name, iscsi_values = self._get_default_3par_iscsi_cinder_conf_section()
        cinder_dict[iscsi_section_name] = iscsi_values

        # 3par FC section
        fc_section_name, fc_values = self._get_default_3par_fc_cinder_conf_section()
        cinder_dict[fc_section_name] = fc_values

        #Create cinder.conf
        self._create_config(self.cinder_config_file,  cinder_dict)


        # Execute the CLI commnad
        command_arvgs=['check', 'array', "-test"]
        cli_exit_value , output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0 , cli_exit_value)
        self.assertEqual( len(output) , 2)


        self._remove_file(self.cinder_config_file)

    @test.attr(type="gate")
    def test_diags_cli_check_sysfsutils_package_command(self) :
        self._check_software_package('sysfsutils')
        self._check_software_package('sg3-utils')


    @test.attr(type="gate")
    def test_diags_cli_check_sg3_utils_package_command(self) :
        self._check_software_package('sg3-utils')



    def _check_software_package(self, package) :

        # Mock permiko ssh client to return cinder file we want
        self._mock_exec_command({"dpkg-query -W -f='${Status} ${Version}' "+ package :'install ok installed 2.2.0'
                                 })


        # Execute the CLI commnad
        command_arvgs=['check', 'software',package,'1.3','-test']
        cli_exit_value , output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0 , cli_exit_value)
        self.assertEqual(len(output) , 1)

        for row in output :
            self.assertEqual(package , row['Software'])
            self.assertEqual('pass' , row['Installed'])
            self.assertEqual('pass' , row['Version'])


         # Mock permiko ssh client to return cinder file we want
        self._mock_exec_command({"dpkg-query -W -f='${Status} ${Version}' "+ package :'no packages found matching  '+package ,
                                 })


        # Execute the CLI commnad
        command_arvgs=['check', 'software',package, '1.3', '-test']
        cli_exit_value , output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0 , cli_exit_value)
        self.assertEqual(len(output) , 1)

        for row in output :
            self.assertEqual(package , row['Software'])
            self.assertEqual('fail' , row['Installed'])
            self.assertEqual('fail' , row['Version'])

          # Mock permiko ssh client to return cinder file we want
        self._mock_exec_command({"dpkg-query -W -f='${Status} ${Version}' " + package:'install ok installed 2.0+repack-3' ,
                                 })


        # Execute the CLI commnad
        command_arvgs=['check', 'software',package, '2.1', '-test']
        cli_exit_value , output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0 , cli_exit_value)
        self.assertEqual(len(output) , 1)

        for row in output :
            self.assertEqual(package , row['Software'])
            self.assertEqual('pass' , row['Installed'])
            self.assertEqual('fail' , row['Version'])

         # Mock permiko ssh client to return cinder file we want
        self._mock_exec_command({"dpkg-query -W -f='${Status} ${Version}' "+package :'Unknown Response' ,
                                 })


        # Execute the CLI commnad
        command_arvgs=['check', 'software',package, '2.1', '-test']
        cli_exit_value , output = self._execute_cli_command(command_arvgs)

        self.assertEqual(0 , cli_exit_value)
        self.assertEqual(len(output) , 1)

        for row in output :
            self.assertEqual(package , row['Software'])
            self.assertEqual('fail' , row['Installed'])
            self.assertEqual('fail' , row['Version'])





    '''
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

    '''


    def _execute_cli_command(self, command_arvgs) :


        cli_dict = { }
        section_name, values = self._get_default_cli_conf_section()
        cli_dict[section_name] = values
        self._create_config('cinderdiags/cli.conf',  cli_dict)

        #open a file to capture the CLI output
        output_file  = self._get_file_name()
        sys.stdout  = open(output_file, 'w')

        cli_exit_value = cli.main(command_arvgs)

        sys.stdout .close()
        output = self._convert_table_output(output_file)

        self._remove_file(output_file)



        return cli_exit_value , output

    def _get_file_name(self):
        return "output.%.7f.txt" % time.time()


    def _remove_file(self, file):

        # remove the file
        if os.path.isfile(file) is True:
               os.remove(file)

    def _convert_table_output(self, filename):

        data = open(filename).read()
        return output_parser.listing(data)



    def _set_ssh_connection_mocks(self):

        client_mock = mock.MagicMock()
        client_mock.connect.return_value = True

        return (self._patch('paramiko.SSHClient'),
                self._patch('paramiko.AutoAddPolicy'),
                client_mock)

    def _mock_ssh_connection(self, config_file, raiseException = 'None'):
         c_mock, aa_mock, client_mock = self._set_ssh_connection_mocks()
         s_mock = self._patch('time.sleep')
         if raiseException == 'None'  :
           c_mock.return_value = client_mock
         else  :
            c_mock.return_value = raiseException


    def _mock_get_file(self, config_file, raiseException = False):
         c_mock, aa_mock, client_mock = self._set_ssh_connection_mocks()
         s_mock = self._patch('time.sleep')
         c_mock.return_value = client_mock

         client_mock.open_sftp.return_value = client_mock

         def my_side_effect(*args, **kwargs):
                 #fromLocation =  args[0]

                 if raiseException :
                     raise Exception()

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
        self.addCleanup(p.stop)
        return m


    def _get_default_3par_iscsi_cinder_conf_section(self) :

        section_name = '3PAR-SLEEPYKITTY'
        dict = {  'volume_driver' : 'cinder.volume.drivers.san.hp.hp_3par_iscsi.HP3PARISCSIDriver',
                  'volume_backend_name' : '3PAR-SLEEPYKITTY',
                  'num_volume_device_scan_tries' : 10,
                  'hp3par_api_url' : 'http://test.ws.url:8080/api/v1',
                  'hp3par_username' : 'testuser',
                  'hp3par_password' : 'testpass',
                  'hp3par_debug' : True,
                  'san_ip': 'http://test.ws.url:8080/api/v1',
                  'san_login' : 'testuser',
                  'san_password' : 'testpass',
                  'hp3par_cpg' : 'testCPG',
                  'hp3par_iscsi_ips' : '1.1.1.1:3260',
                  'hp3par_iscsi_chap_enabled' : 'false' }
        return section_name , dict

    def _get_default_3par_fc_cinder_conf_section(self) :

        section_name = '3PAR-SLEEPYKITTY-FC'
        dict = {  'volume_driver' : 'cinder.volume.drivers.san.hp.hp_3par_fc.HP3PARFCDriver',
                  'volume_backend_name' : '3PAR-SLEEPYKITTY-FC',
                  'hp3par_api_url' : 'http://test.ws.url:8080/api/v1',
                  'hp3par_username' : 'testuser',
                  'hp3par_password' : 'testpass',
                  'hp3par_debug' : True,
                  'san_ip': 'http://test.ws.url:8080/api/v1',
                  'san_login' : 'testuser',
                  'san_password' : 'testpass',
                  'hp3par_cpg' : 'testCPG'
                               }


        return section_name , dict


    def _get_default_cli_conf_section(self) :

        section_name = 'TEST'
        dict = {  'service' : 'test',
                  'host_ip' : '192.168.10.5',
                  'ssh_user' : 'vagrant',
                  'ssh_password' : 'vagrant',
                  'conf_source' : '/etc/cinder/cinder.conf'
                   }

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


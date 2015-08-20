
import mock
import time
import ConfigParser
import os
from sshClient import Client
import pkg_checks
from tempest.api.volume import base
from tempest import test
from tempest import config

CONF = config.CONF

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





    def _set_ssh_connection_mocks(self):

        client_mock = mock.MagicMock()
        client_mock.connect.return_value = True

        return (self._patch('paramiko.SSHClient'),
                self._patch('paramiko.AutoAddPolicy'),
                client_mock)


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


    def _inject_error_in_cinder_configuration(self , dict, section) :

	   if os.path.isfile(self.cinder_config):

                try :
                   config = ConfigParser.RawConfigParser(allow_no_value=True)
                   config.read(self.cinder_config)
                   if config.has_section(section):
                      for key in dict.keys():
                          config.set(section,key,dict.get(key))
                   else :
                      print "Cinder conf does not cotanin the 3PAR configuration "
                   # Writing our configuration file to 'cinder.conf'
                   with open(self.cinder_config, 'w') as configfile:
                        config.write(configfile)
                   self.restart_cinder_service();
                   time.sleep(15)
                except Exception as e : # catch *all* exceptions
                    raise e
           else :
                 print "No file present : " + self.cinder_config



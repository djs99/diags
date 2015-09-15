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
import ConfigParser
import os

class BaseCinderDiagnosticsCliToolTest(unittest.TestCase):

    """Base test case class for all 3PAR cinder Diagnostics CLI Tool """


    def _set_ssh_connection_mocks(self):

        client_mock = mock.MagicMock()
        client_mock.connect.return_value = True

        return (self._patch('paramiko.SSHClient'),
                self._patch('paramiko.AutoAddPolicy'),
                client_mock)

    def setUp(self):
         self.mock_instances = []

    def tearDown(self) :
         for mock_instance in self.mock_instances :
             mock_instance.stop()


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
        """
        Returns a started `mock.patch` object for the supplied target.

        The caller may then call the returned patcher to create a mock object.

        The caller does not need to call stop() on the returned
        patcher object, as this method automatically adds a cleanup
        to the test class to stop the patcher.

        :param target: String module.class or module.object expression to patch
        :param **kwargs: Passed as-is to `mock.patch`. See mock documentation
                         for details.
        """
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



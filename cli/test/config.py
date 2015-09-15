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

__all__ = ['Config']

import ConfigParser
import os.path

class Config(object):
    """Singleton to store global config values
    """
    _instance = None

    cinder_hostname = None
    cinder_ssh_username = None
    cinder_ssh_password = None
    nova_hostname = None
    nova_ssh_username = None
    nova_ssh_password = None
  
    api_version = None
    os_username = None
    os_password = None
    os_auth_url = None
    os_project_name = None
#    cinderLogLocation = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            # initializing intance 
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)

            # Parse configuration from command line and config file
            #---------------------------------------------------------------------------------------
            # Pull in configuration from config file
            if os.path.isfile("Properties.cfg"):
                config = ConfigParser.RawConfigParser()
                config.read("Properties.cfg")
                if config.has_option('Devstack', 'devstack_host'): Config().cinder_hostname = config.get('Devstack', 'devstack_host')
                if config.has_option('Devstack', 'devstack_ssh_username'): Config().cinder_ssh_username = config.get('Devstack', 'devstack_ssh_username')
                if config.has_option('Devstack', 'devstack_ssh_password'): Config().cinder_ssh_password = config.get('Devstack', 'devstack_ssh_password')
               
                if config.has_option('Devstack', 'devstack_host'): Config().nova_hostname = config.get('Devstack', 'devstack_host')
                if config.has_option('Devstack', 'devstack_ssh_username'): Config().nova_ssh_username = config.get('Devstack', 'devstack_ssh_username')
                if config.has_option('Devstack', 'devstack_ssh_password'): Config().nova_ssh_password = config.get('Devstack', 'devstack_ssh_password')
                
                if config.has_option('Identity', 'api_version'): Config().api_version = config.get('Identity', 'api_version') 
                if config.has_option('Identity', 'username'): Config().os_username = config.get('Identity', 'username') 
                if config.has_option('Identity', 'password'): Config().os_password = config.get('Identity', 'password')
                if config.has_option('Identity', 'auth_url'): Config().os_auth_url = config.get('Identity', 'auth_url')
                if config.has_option('Identity', 'project_name'): Config().os_project_name = config.get('Identity', 'project_name')
            
        return cls._instance


    def PrintUserSetConfigs(self):
        just=20
        print("{0:<{2}}: {1}".format("Devstack VM", self.cinder_hostname, just))
        print("{0:<{2}}: {1}".format("Devstack SSH User", self.cinder_ssh_username, just))
        print("{0:<{2}}: {1}".format("Devstack SSH Password", self.cinder_ssh_password, just))
      
#	print("{0:<{2}}: {1}".format("Cinder Log Location", self.cinderLogLocation, just))
CONF = Config()

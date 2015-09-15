__all__ = ['Config']

import ConfigParser
import os.path

class Config(object):
    """Singleton to store global config values
    """
    _instance = None

    devstackVM = None
    devstackSshUser = None
    devstackSshPassword = None
  
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
                if config.has_option('Devstack', 'devstack_host'): Config().devstackVM = config.get('Devstack', 'devstack_host') 
                if config.has_option('Devstack', 'devstack_ssh_username'): Config().devstackSshUser = config.get('Devstack', 'devstack_ssh_username') 
                if config.has_option('Devstack', 'devstack_ssh_password'): Config().devstackSshPassword = config.get('Devstack', 'devstack_ssh_password') 
               
               
                
                if config.has_option('Identity', 'api_version'): Config().api_version = config.get('Identity', 'api_version') 
                if config.has_option('Identity', 'username'): Config().os_username = config.get('Identity', 'username') 
                if config.has_option('Identity', 'password'): Config().os_password = config.get('Identity', 'password')
                if config.has_option('Identity', 'auth_url'): Config().os_auth_url = config.get('Identity', 'auth_url')
                if config.has_option('Identity', 'project_name'): Config().os_project_name = config.get('Identity', 'project_name')
            
        return cls._instance


    def PrintUserSetConfigs(self):
        just=20
        print("{0:<{2}}: {1}".format("Devstack VM", self.devstackVM, just))
        print("{0:<{2}}: {1}".format("Devstack SSH User", self.devstackSshUser, just))
        print("{0:<{2}}: {1}".format("Devstack SSH Password", self.devstackSshPassword, just))
      
#	print("{0:<{2}}: {1}".format("Cinder Log Location", self.cinderLogLocation, just))
       


from sshClient import Client
import config as config
from base import *
import os
import time

CONF = config.CONF

class CinderDiagnostics3PARCliSshClientTest(BaseCinderDiagnosticsCliToolTest):
    """
    This testclass is wrriten to test the  SSH client of 3PAR cinder diagnostics CLI tool

    """
    @classmethod
    def setUpClass(cls):
        super(BaseCinderDiagnosticsCliToolTest, cls).setUpClass()


    def test_ssh_connection(self) :
        """ Test SSH Connection to cinder node """
        client = None
        try :
            client = Client(CONF.cinder_hostname, CONF.cinder_ssh_username, CONF.cinder_ssh_password)
            output = client.execute('echo Successful')
            self.assertEqual(output, "Successful")
        except Exception :
            self.fail("Connection unSuccessful" )
        finally:
            if client is not None :
                client.disconnect()

    def test_get_file(self) :
        """ Test SSH Connection to cinder node """
        client = None
        temp_file = temp = "report.%.7f.conf" % time.time()
        try :
            client = Client(CONF.cinder_hostname, CONF.cinder_ssh_username, CONF.cinder_ssh_password)
            client.get_file('/etc/cinder/cinder.conf', temp_file)
            self.assertEqual(True,os.path.isfile(temp_file))
        except Exception :
            self.fail("Failed to get the file" )
        finally:
            if client is not None :
                client.disconnect()
            if os.path.isfile(temp_file) is True:
                os.remove(temp_file)



if __name__ == '__main__':
    unittest.main()
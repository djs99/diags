
from tempest import config
from sshClient import Client
from tempest.api.volume import base
from tempest import test
import time
import os
CONF = config.CONF

class CinderDiagnostics3PARCliSshClientToolTest(base.BaseVolumeAdminTest):

    """Base test case class for all 3PAR cinder Diagnostics CLI Tool """


    @classmethod
    def resource_setup(cls):
        super(CinderDiagnostics3PARCliSshClientToolTest, cls).resource_setup()

    @test.attr(type="gate")
    def test_ssh_connection(self) :
        """ Test SSH Connection to cinder node """
        client = None

        try :
            client = Client(CONF.cinder_hostname, CONF.cinder_ssh_username, CONF.cinder_ssh_password)
            output = client.execute('echo Successful')
            self.assertEqual(output, "Successful\n")

        except Exception as e:
            self.fail("Connection unSuccessful " + e.message)

        finally:
            if client is not None :
                client.disconnect()
    @test.attr(type="gate")
    def test_get_file(self) :
        """ Test SSH Connection to cinder node """
        client = None
        temp_file = temp = "report.%.7f.conf" % time.time()

        try :
            client = Client(CONF.cinder_hostname, CONF.cinder_ssh_username, CONF.cinder_ssh_password)
            client.get_file('/etc/cinder/cinder.conf', temp_file)
            self.assertEqual(True,os.path.isfile(temp_file))

        except Exception as e:
            self.fail("Failed to get the file " + e.message)

        finally:
            if client is not None :
                client.disconnect()
            if os.path.isfile(temp_file) is True:
                os.remove(temp_file)
    @test.attr(type="gate")
    def test_get_unkown_file(self) :
        """ Test SSH Connection to cinder node """
        client = None
        temp_file = temp = "report.%.7f.conf" % time.time()

        try :
            client = Client(CONF.cinder_hostname, CONF.cinder_ssh_username, CONF.cinder_ssh_password)
            client.get_file('/etc/cinder/cinder_not_present.conf', temp_file)
            self.fail()

        except Exception as e:
            self.assertEqual(False,os.path.isfile(temp_file))

        finally:
            if client is not None :
                client.disconnect()
            if os.path.isfile(temp_file) is True:
                os.remove(temp_file)

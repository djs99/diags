import unittest
import sshClient
from Config import *




class CinderErrorTest(unittest.TestCase):
    
  def test_3par_bad_credential(self):
    # First inject 3par bad credential error 
    filesToCopy = ["ErrorInjection.py"]
    response = sshClient.executeCommand(Config().devstackVM, Config().devstackSshUser, Config().devstackSshPassword, "python ErrorInjection.py --bad_3par_credential", filesToCopy)
    self.assertEqual("Error bad_3par_credential Injected Successfully \n",response[0]) 

  def test_3par_bad_cpg(self):
    # First inject 3par bad credential error
    filesToCopy = ["ErrorInjection.py"]
    response = sshClient.executeCommand(Config().devstackVM, Config().devstackSshUser, Config().devstackSshPassword, "python ErrorInjection.py --bad_3par_cpg", filesToCopy)
    self.assertEqual("Error bad_3par_cpg Injected Successfully \n",response[0])
  def test_missing_package_3parclient(self):
    # First inject 3par bad credential error
    filesToCopy = ["ErrorInjection.py"]
    response = sshClient.executeCommand(Config().devstackVM, Config().devstackSshUser, Config().devstackSshPassword, "python ErrorInjection.py --missing_package_3parclient", filesToCopy)
    self.assertEqual("Error missing_package_3parclient Injected Successfully \n",response[0])
    
  def test_bad_3par_iscsi_ips(self):
    # First inject bad_3par_iscsi_ips error
    filesToCopy = ["ErrorInjection.py"]
    response = sshClient.executeCommand(Config().devstackVM, Config().devstackSshUser, Config().devstackSshPassword, "python ErrorInjection.py --bad_3par_iscsi_ips", filesToCopy)
    self.assertEqual("Error bad_3par_iscsi_ips Injected Successfully \n",response[0])


if __name__ == '__main__':
    unittest.main()

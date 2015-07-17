import base
import unittest
import time
import sshClient
from Config import Config

class BadCredentialsTest(base.BaseCinderDiagnosticsTest):

      def test_cinder_credentials(self):
      
      
        metric_name = 'cinderDiagnostics.credentials'
        error_injection_name = 'bad_3par_credential'
        alarm_description =  'Bad 3PAR Credentials'
        
        print "running functional test case " + metric_name
        self.run_functional_testcase(metric_name, alarm_description, error_injection_name)
        
        
        
if __name__ == '__main__':
    unittest.main()

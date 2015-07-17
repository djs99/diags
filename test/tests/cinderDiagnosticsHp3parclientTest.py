import base
import unittest
import time
import sshClient
from Config import Config

class BadHP3PARClientTest(base.BaseCinderDiagnosticsTest):

      def test_missing_package_3parclient(self):
        
       
       metric_name = 'cinderDiagnostics.3par'
       error_injection_name = 'missing_package_3parclient'
       alarm_description =  'Missing hp3parclient'
        
       print "running functional test case " + metric_name
       self.run_functional_testcase(metric_name, alarm_description, error_injection_name)
       


if __name__ == '__main__':
    unittest.main()

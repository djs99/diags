import base
import unittest
import time


class BadCPGTest(base.BaseCinderDiagnosticsTest):
     
      def test_cinder_cpg(self):
      
       metric_name = 'cinderDiagnostics.CPG'
       error_injection_name = 'bad_3par_cpg'
       alarm_description =  'Bad 3PAR CPG'
        
       print "running functional test case " + metric_name
       self.run_functional_testcase(metric_name, alarm_description, error_injection_name)
      
      


if __name__ == '__main__':
    unittest.main()

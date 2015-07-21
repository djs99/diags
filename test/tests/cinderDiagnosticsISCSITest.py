import base
import unittest
import time
import sshClient
from Config import Config

class BadISCSITest(base.BaseCinderDiagnosticsTest):

      def test_cinder_iscsi_ips(self):


        metric_name = 'cinderDiagnostics.iSCSI'
        error_injection_name = 'bad_3par_iscsi_ips'
        alarm_description =  'Bad 3PAR ISCSI IPs'

        print "running functional test case " + metric_name
        self.run_functional_testcase(metric_name, alarm_description, error_injection_name)



if __name__ == '__main__':
    unittest.main()



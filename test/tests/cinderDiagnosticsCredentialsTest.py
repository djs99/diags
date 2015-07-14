import base
import unittest
import time
import sshClient
from Config import Config

class BadCredentialsTest(base.BaseCinderDiagnosticsTest):

      def test_cinder_cpg(self):
        
        # List metric by metric name
        metric_name = 'storageDiagnostics.credentials'
        fields = {'name': metric_name}
        fields['timestamp'] = int((time.time()*1000))
        response = self.call(self.monitoring_client.metrics.list ,fields)
        self.assertEquals(metric_name, response[0]['name'])
        self.assertEquals('Forbidden_HTTP_403_5_-_invalid_username_or_password', response[0]['dimensions']['error'])
        
        
        metric_start_time = time.time()
        metric_end_time = time.time()
        if (metric_end_time - metric_start_time) < 1:
            metric_end_time = metric_start_time + 1
        fields = {'name': metric_name}
        fields['end_time'] = self.create_timestamp(metric_end_time)
        fields['start_time'] = self.create_timestamp(metric_start_time)
        fields['timestamp'] = int((time.time()*1000))
        fields['merge_metrics'] = 'true'
        response = self.call(self.monitoring_client.metrics.list_measurements ,fields)
        self.assertEquals(metric_name, response[0]['name'])
        self.assertEquals({}, response[0]['dimensions'])
        self.assertEquals([], response[0]['measurements'])
        self.assertEquals(None, response[0]['id'])
        
        print response       
        
        # First inject 3par bad credential error
        filesToCopy = ["ErrorInjection.py"]
        response = sshClient.executeCommand(Config().devstackVM, Config().devstackSshUser, Config().devstackSshPassword, "python ErrorInjection.py --bad_3par_credential", filesToCopy)
        self.assertEqual("Error bad_3par_credential Injected Successfuly \n",response[0])
         # First inject 3par bad credential error
 
        
        metric_end_time = time.time()
        fields = {'name': metric_name}
        fields['end_time'] = self.create_timestamp(metric_end_time)
        fields['start_time'] = self.create_timestamp(metric_start_time)
        fields['timestamp'] = int((time.time()*1000))
        fields['merge_metrics'] = 'true'
       
        #self.assertEquals(metric_name, response[0]['name'])
        #self.assertEquals({}, response[0]['dimensions'])
        #self.assertEquals([], response[0]['measurements'])
        #self.assertEquals(None, response[0]['id'])
        
        for i in range(0, 30):
            response = self.call(self.monitoring_client.metrics.list_measurements ,fields)
            print response
            if len(response[0]['measurements']) == 1:
                break 
            time.sleep(2)

        if len(response[0]['measurements']) == 0:
             self.fail("No measurements found for " + metric_name )
        
        
        
if __name__ == '__main__':
    unittest.main()

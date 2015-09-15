
import base
import unittest
import time 

class CinderMetricTest(base.BaseCinderDiagnosticsTest):

    def test_metric_cinder_cpg(self):
        # List metric by metric name
        metric_name = 'storageDiagnostics.CPG'
        fields = {'name': metric_name}
        fields['timestamp'] = int((time.time()*1000))
        response = self.call(self.monitoring_client.metrics.list ,fields)
        self.assertEquals(metric_name, response[0]['name'])
        self.assertEquals('Invalid_input_received:_CPG', response[0]['dimensions']['error'])
    def test_metric_cinder_credentail(self):
        # List metric by metric name
        metric_name = 'storageDiagnostics.credentials'
        fields = {'name': metric_name}
        fields['timestamp'] = int((time.time()*1000))
        response = self.call(self.monitoring_client.metrics.list ,fields)
	self.assertEquals(metric_name, response[0]['name'])
	self.assertEquals('Forbidden_HTTP_403_5_-_invalid_username_or_password', response[0]['dimensions']['error'])

    def test_measurements_cinder_credentail(self):
        # List metric by metric measurements name
        metric_name = 'storageDiagnostics.credentials'
        metric_end_time = time.time()
        metric_start_time = time.time()-100
        fields = {'name': metric_name}
        fields['end_time'] = self.create_timestamp(metric_end_time)
        fields['start_time'] = self.create_timestamp(metric_start_time)
        fields['timestamp'] = int((time.time()*1000))
        response = self.call(self.monitoring_client.metrics.list_measurements ,fields)
	self.assertEquals(metric_name, response[0]['name'])
	self.assertEquals('Forbidden_HTTP_403_5_-_invalid_username_or_password', response[0]['dimensions']['error'])
        print response
    def test_measurements_cinder_cpg(self):
        # List metric by metric measurements name
        metric_name = 'storageDiagnostics.CPG'
        metric_end_time = time.time()
        metric_start_time = time.time()-100
        fields = {'name': metric_name}
        fields['end_time'] = self.create_timestamp(metric_end_time)
        fields['start_time'] = self.create_timestamp(metric_start_time)
        fields['timestamp'] = int((time.time()*1000))
        fields['merge_metrics'] = 'true'
        response = self.call(self.monitoring_client.metrics.list_measurements ,fields)
#	print response
	self.assertEquals(metric_name, response[0]['name'])
#	self.assertEquals('Invalid_input_received:_CPG', response[0]['dimensions']['error'])
#	print response[0]['dimensions']['error']
	#print response[0]['dimensions'].keys()
        #self.assertEquals(m_name, response['elements'][0]['name'])
        #self.assertEqual('200', body.response['status'])




if __name__ == '__main__':
    unittest.main()

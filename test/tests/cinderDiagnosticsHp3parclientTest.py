import base
import unittest
import time
import sshClient
from Config import Config

class BadHP3PARClientTest(base.BaseCinderDiagnosticsTest):

      def test_missing_package_3parclient(self):
        
        # List metric by metric name
        metric_name = 'cinderDiagnostics.3par'
        fields = {'name': metric_name}
        fields['timestamp'] = int((time.time()*1000))
        response = self.call(self.monitoring_client.metrics.list ,fields)
        if len(response) > 0 :
           self.assertEquals(metric_name, response[0]['name'])
           self.assertEquals('You_must_install_hp3parclient_before_using_3PAR_drivers', response[0]['dimensions']['error'])
        else :
           self.fail("No metric " + metric_name + " found " )
      
        notification_name = 'notification-cpg'
        notification_address = 'root@localhost'
        notification_id = None
        notification = self.find_notification_by_name(notification_name)
        if notification is None :
            notification_id = self.create_notification(notification_name, notification_address)
        else :
            notification_id = notification['id']
          
        
        
        alarm_name = metric_name
        expression = 'cinderDiagnostics.3par > 0'
        description = 'Bad 3PAR CPG' 
        severity = 'HIGH'
        alarm_definations = self.find_alarm_defination_byname(alarm_name)
        alarm_id =  None
        if alarm_definations is None :
            alarm_id = self.create_alarm_defination(alarm_name, description, expression, severity, notification_id, notification_id, notification_id)
        else :
            alarm_id = alarm_definations['id']
        
#        self.enable(alarm_id)
        
        metric_start_time = time.time()
        metric_end_time = time.time()
        if (metric_end_time - metric_start_time) < 1:
            metric_end_time = metric_start_time + 1 


        fields = {'name': metric_name}
        fields['end_time'] = self.create_timestamp(metric_end_time)
        fields['start_time'] = self.create_timestamp(metric_start_time);
        fields['timestamp'] = int((time.time()*1000))
        fields['merge_metrics'] = 'true'
        response = self.call(self.monitoring_client.metrics.list_measurements ,fields)
        self.assertEquals(metric_name, response[0]['name'])
        self.assertEquals({}, response[0]['dimensions'])
        self.assertEquals([], response[0]['measurements'])
        self.assertEquals(None, response[0]['id'])
        
        print response       
        
        # First inject missing_package_3parclient error
        filesToCopy = ["ErrorInjection.py"]
        response = sshClient.executeCommand(Config().devstackVM, Config().devstackSshUser, Config().devstackSshPassword, "python ErrorInjection.py --missing_package_3parclient", filesToCopy)
        self.assertEqual("Error missing_package_3parclient Injected Successfully \n",response[0])
        
        # Add sleep if you are commenting the error injection
        #time.sleep(2)        
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
        
 #       alarms = self.get_alarm(alarm_id)
 #       for alarm in alarms:
 #         print alarm 
 #         print  "\n\n"



if __name__ == '__main__':
    unittest.main()

import utils
import time
import unittest
import pytz
from datetime import datetime
import monascaclient.exc as exc
import sshClient
from Config import Config

class BaseCinderDiagnosticsTest(unittest.TestCase):

    """Base test case class for all Monitoring API tests."""
     
    monitoring_client = None

    @classmethod
    def setUpClass(cls):
         
       cls.monitoring_client = utils.create_monasca_client()
    
    @classmethod    
    def create_timestamp(self, seconds):
      utcTimestamp = pytz.utc.localize(datetime.utcfromtimestamp(seconds))
      return utcTimestamp.strftime("%Y-%m-%dT%H:%M:%S%z")
    
   
    def run_functional_testcase(self , metric_name , alarm_description , error_injection_name ) :  
       # List metric by metric name
       
        fields = {'name': metric_name}
        fields['timestamp'] = int((time.time()*1000))
        response = self.call(self.monitoring_client.metrics.list ,fields)
        if len(response) > 0 :
           self.assertEquals(metric_name, response[0]['name'])
           #self.assertEquals(error_description, response[0]['dimensions']['error'])
        else :
           self.fail("No metric " + metric_name + " found " )
      
        notification_name = metric_name
        notification_address = 'root@localhost'
        notification_id = None
        notification = self.find_notification_by_name(notification_name)
        if notification is None :
            notification_id = self.create_notification(notification_name, notification_address)
        else :
            notification_id = notification['id']
          
        
        alarm_name = metric_name
        expression = '%s > 0' % (metric_name)

        description = alarm_description 
        severity = 'HIGH'
        alarm_definations = self.find_alarm_defination_byname(alarm_name)
        alarm_definations_id =  None
        if alarm_definations is None :
            alarm_definations_id = self.create_alarm_defination(alarm_name, description, expression, severity, notification_id, notification_id, notification_id)
        else :
            alarm_definations_id = alarm_definations['id']
      
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
        
        # First inject 3par bad credential error
        filesToCopy = ["ErrorInjection.py"]
        response = sshClient.executeCommand(Config().devstackVM, Config().devstackSshUser, Config().devstackSshPassword, "python ErrorInjection.py --"+error_injection_name, filesToCopy)
        self.assertEqual("Error "+error_injection_name+" Injected Successfully \n",response[0])
        
        # Add sleep if you are commenting the error injection
        #time.sleep(2)        
        metric_end_time = time.time()
        fields = {'name': metric_name}
        fields['end_time'] = self.create_timestamp(metric_end_time)
        fields['start_time'] = self.create_timestamp(metric_start_time)
        fields['timestamp'] = int((time.time()*1000))
        fields['merge_metrics'] = 'true'
        
        isMeasurementsFound = False
        isAlarmFound = False
        isStateChangeToAlarm = False
        
        for i in range(0, 30):
            response = self.call(self.monitoring_client.metrics.list_measurements ,fields)
            if len(response[0]['measurements']) == 1:
                isMeasurementsFound = True ;
                break 
            time.sleep(2)
        
        for i in range(0, 60):
            response = self.find_alarm_by_definition_id(alarm_definations_id)
            if response is not None:
               isAlarmFound = True
               if response['state'] == 'ALARM' :
                  isStateChangeToAlarm = True
                  break 
            time.sleep(3)
        
        
        if not isMeasurementsFound and not isStateChangeToAlarm :
             self.fail("No measurements found for " + metric_name )
        if not isAlarmFound :
             self.fail("No alarm found for " + metric_name )
        if not isStateChangeToAlarm :
             self.fail("No state change to ALARM  for  metric " + metric_name )
   
   
    @classmethod      
    def call(self, method, fields):
       try:
           resp = method(**fields)
#	   print(resp[0]['dimensions'][u'error'])
#	   print resp[0]['dimensions'][u'error_type']
       except exc.HTTPException as he:
           print(he.code)
           print(he.message)
           raise he
       else:
           return resp
    @classmethod
    def get_state(self, alarm_id):
        result = self.get(alarm_id)
        return result['state']

    @classmethod
    def get_alarm(self, alarm_id):
        result = self.monitoring_client.alarms.get(**{'alarm_id': alarm_id})
        return result

    @classmethod
    def disable(self, alarm_id):
        self.patch(alarm_id, {'actions_enabled': False})

    @classmethod
    def enable(self, alarm_id):
        self.patch(alarm_id, {'actions_enabled': True})

    @classmethod
    def set_state(self, alarm_id, state):
        self.patch( alarm_id, {'state': state})
        new_state = self.get_state(alarm_id)
        if new_state != state:
            return False
        return True

    @classmethod
    def patch(self, alarm_id, fields):
         fields['alarm_id'] = alarm_id
         self.monitoring_client.alarms.patch(**fields)

    @classmethod
    def set_optional_field(self, name, value, fields):
        if value is not None:
           fields[name] = value

    @classmethod
    def create_alarm_defination(self, name, description, expression, severity, ok_actions=None,
           alarm_actions=None, undetermined_actions=None):
        fields = {}
        fields['name'] = name
        fields['expression'] = expression
        self.set_optional_field('description', description, fields)
        self.set_optional_field('severity', severity, fields)
        self.set_optional_field('ok_actions', ok_actions, fields)
        self.set_optional_field('alarm_actions', alarm_actions, fields)
        self.set_optional_field('undetermined_actions', undetermined_actions, fields)
        result = self.monitoring_client.alarm_definitions.create(**fields)
        return result['id']


    def find_alarm_defination_byname(self, alarm_name):
        alarms = self.monitoring_client.alarm_definitions.list(**{})
        for alarm in alarms:
           if alarm['name'] == alarm_name:
              return alarm
        return None
    
    def find_alarm_by_definition_id(self, alarm_definition_id):
        alarms = self.monitoring_client.alarms.list(**{})
        for alarm in alarms:
           if alarm['alarm_definition']['id'] == alarm_definition_id :
              return alarm
        return None    


    @classmethod
    def create_notification(self, name, email):
        kwargs = {'name': name, 'address': email, 'type': 'EMAIL'}
        result = self.monitoring_client.notifications.create(**kwargs)
        return result['id']
    
    @classmethod
    def update_notification(self, notification_id, name, email):
        kwargs = {'id': notification_id, 'name': name, 'address': email,
                  'type': 'EMAIL'}
        result = mon_client.notifications.update(**kwargs)
        return result['id']
    
    @classmethod
    def get_notification(self, notification_id):
        kwargs = {'notification_id': notification_id}
        result = self.monitoring_client.notifications.get(**kwargs)
        return result
    
    @classmethod
    def find_notification_by_name(self, name):
        result = self.monitoring_client.notifications.list(**{})
        for notification in result:
            if notification['name'] == name:
                return notification
        return None
    
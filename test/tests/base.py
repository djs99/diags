import utils
import time
import json
import unittest
import pytz
import sys
from datetime import datetime
import monascaclient.exc as exc

class BaseCinderDiagnosticsTest(unittest.TestCase):

    """Base test case class for all Monitoring API tests."""
     
    monitoring_client = None

    @classmethod
    def setUpClass(cls):
         
       cls.monitoring_client = utils.create_monasca_client()
    
    @classmethod
    def deserialize(self, body):
        return json.loads(body.replace("\n", ""))
    @classmethod
    def serialize(self, body):
        return json.dumps(body)
    @classmethod    
    def create_timestamp(self, seconds):
      utcTimestamp = pytz.utc.localize(datetime.utcfromtimestamp(seconds))
      return utcTimestamp.strftime("%Y-%m-%dT%H:%M:%S%z")
    
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
        result = get(alarm_id)
        return result['state']

    @classmethod
    def get_alarm(self, alarm_id):
        result = self.monitoring_client.alarms.get(**{'alarm_id': alarm_id})
        return result

    @classmethod
    def disable(self, alarm_id):
        patch(alarm_id, {'actions_enabled': False})

    @classmethod
    def enable(self, alarm_id):
        patch(alarm_id, {'actions_enabled': True})

    @classmethod
    def set_state(self, alarm_id, state):
        patch( alarm_id, {'state': state})
        new_state = get_state(alarm_id)
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

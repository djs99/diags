from __future__ import print_function
import time
import datetime
from oslo_serialization import jsonutils as json
from monascaclient import client
from monascaclient import ksclient
"""
     methods for testing
"""
api_version = '2_0'
OS_USERNAME = 'mini-mon'
OS_PASSWORD = 'password'
OS_PROJECT_NAME = 'mini-mon'
OS_AUTH_URL = 'http://192.168.10.5:35357/v3/'


def create_monasca_client() :
    ks = ksclient.KSClient(auth_url=OS_AUTH_URL, username=OS_USERNAME, password=OS_PASSWORD)
    return client.Client(api_version, ks.monasca_url, token=ks.token)
  
def deserialize(body):
    return json.loads(body.replace("\n", ""))
    
def serialize(self, body):
    return json.dumps(body)
            


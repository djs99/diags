from __future__ import print_function
import time
import datetime
from oslo_serialization import jsonutils as json
from monascaclient import client
from monascaclient import ksclient
from Config import Config
"""
     methods for testing
"""
api_version = Config().api_version
OS_USERNAME = Config().os_username
OS_PASSWORD = Config().os_password
OS_PROJECT_NAME = Config().os_project_name
OS_AUTH_URL = Config().os_auth_url


def create_monasca_client() :
    ks = ksclient.KSClient(auth_url=OS_AUTH_URL, username=OS_USERNAME, password=OS_PASSWORD)
    return client.Client(api_version, ks.monasca_url, token=ks.token)
  
def deserialize(body):
    return json.loads(body.replace("\n", ""))
    
def serialize(self, body):
    return json.dumps(body)
            


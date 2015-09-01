"""
This fakes 3PAR REST API Client behavior to allow for testing of the Cinder
Diagnostics tool without access to a 3PAR array
"""
# -----------------------------------------------------------
import sys
sys.path.append('/usr/local/lib/python2.7/dist-packages')
# -----------------------------------------------------------
from hp3parclient import exceptions


class HP3ParClient(object):

    PORT_MODE_TARGET = 2
    PORT_PROTO_ISCSI = 2
    PORT_STATE_READY = 4

    API_URL = 'http://test.ws.url:8080/api/v1'
    USERNAME = 'testuser'
    PASSWORD = 'testpass'
    CPG = 'testCPG'

    def __init__(self, api_url):
        if api_url == self.API_URL:
            pass
        else:
            raise exceptions.HTTPBadRequest('Error communicating with the 3PAR WS')

    def login(self, username, password):
        if username == self.USERNAME and password == self.PASSWORD:
            pass
        else:
            raise exceptions.HTTPUnauthorized('invalid username or password')

    def logout(self):
        pass

    def getCPG(self, name):
        if name == self.CPG:
            pass
        else:
            raise exceptions.HTTPNotFound('Invalid input received: CPG')

    def getPorts(self):
        first = {'mode': self.PORT_MODE_TARGET,
                 'linkState': self.PORT_STATE_READY,
                 'protocol': self.PORT_PROTO_ISCSI,
                 'IPAddr': '1.1.1.1'
                 }
        second = {'mode': self.PORT_MODE_TARGET,
                 'linkState': self.PORT_STATE_READY,
                 'protocol': self.PORT_PROTO_ISCSI,
                 'IPAddr': '2.2.2.2'
                  }
        ports = {'members': [first, second]}
        return ports

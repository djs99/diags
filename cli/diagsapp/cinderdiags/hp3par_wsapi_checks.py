"""
This checks the cinder.conf file to find errors in the configuration of 3PAR
arrays.

Requires the python hp3parclient: sudo pip install hp3parclient
Assumes the volume_driver is correctly set
"""
from __future__ import absolute_import

import logging
# from oslo_utils import importutils
from six.moves import configparser
from . import hp3par_testclient as testclient

logger = logging.getLogger(__name__)

try:
    from hp3parclient import client as hpclient
    from hp3parclient import exceptions as hpexceptions
except ImportError:
    logger.error('hp3parclient package not found (pip install hp3parclient)')
# hp3parclient = importutils.try_import("hp3parclient")
# if hp3parclient:
#     from hp3parclient import client as hpclient
#     from hp3parclient import exceptions as hpexceptions
#     from . import hp3par_testclient as testclient
# else:
#     raise ImportError('hp3parclient package is not installed')



class WSChecker(object):

    def __init__(self, client, conf, node, test=False):
        """Tests web service api configurations in the cinder.conf file

        :param conf: location of cinder.conf
        :param node: cinder node the cinder.conf was copied from
        :param test: use testing client
        """
        self.conf = conf
        self.ssh_client = client
        self.node = node
        self.is_test = test
        self.parser = configparser.ConfigParser()
        self.parser.read(self.conf)
        self.hp3pars = []
        for section in self.parser.sections():
            if self.parser.has_option(section, 'volume_driver') \
                    and 'hp_3par' in self.parser.get(section, 'volume_driver'):
                self.hp3pars.append(section)

    def check_all(self):
        """Tests configuration settings for all 3par arrays

        :return: a list of dictionaries
        """
        all_tests = []
        for section_name in self.hp3pars:
            all_tests.append(self.check_section(section_name))
        return all_tests

    def check_section(self, section_name):
        """Runs all WS configuration tests for a section

        :param section_name: from cinder.conf as [SECTION_NAME]
        :return: a dictionary - each property is pass/fail/unknown
        """
        tests = {
            "name": section_name,
            "url": "unknown",
            "credentials": "unknown",
            "cpg": "unknown",
            "iscsi": "unknown",
            "node": self.node,
            "driver": "unknown"
        }
        if section_name in self.hp3pars:
            tests["driver"] = self.has_driver(section_name)
            client = self.get_client(section_name, self.is_test)
            if client:
                tests["url"] = "pass"
                if self.cred_is_valid(section_name, client):
                    tests["credentials"] = "pass"
                    tests["cpg"] = self.cpg_is_valid(section_name, client)
                    if 'iscsi' in self.parser.get(section_name,
                                                  'volume_driver'):
                        tests["iscsi"] = self.iscsi_is_valid(section_name,
                                                             client)
                    client.logout()
                else:
                    tests["credentials"] = "fail"

            else:
                tests["url"] = "fail"
            if 'hp_3par_fc' in self.parser.get(section_name, 'volume_driver'):
                tests["iscsi"] = "N/A"
            return tests
        else:
            return None


# Config testing methods check if option values are valid
    def get_client(self, section_name, test):
        """Tries to create a client and verifies the api url

        :return: The client if url is valid, None if invalid/missing
        """
        try:
            if test:
                cl = testclient.HP3ParClient(self.parser.get(section_name,
                                                             'hp3par_api_url'))
            else:
                cl = hpclient.HP3ParClient(self.parser.get(section_name,
                                                           'hp3par_api_url'))

            return cl
        except (hpexceptions.UnsupportedVersion, hpexceptions.HTTPBadRequest,
                configparser.NoOptionError, TypeError):
            return None

    def cred_is_valid(self, section_name, client):
        """Tries to login to the client to verify credentials

        :return: True if credentials are valid, False if invalid/missing
        """
        try:
            client.login(self.parser.get(section_name, 'hp3par_username'),
                         self.parser.get(section_name, 'hp3par_password'))
            return True
        except (hpexceptions.HTTPForbidden,
                hpexceptions.HTTPUnauthorized,
                configparser.NoOptionError):
            return False

    def cpg_is_valid(self, section_name, client):
        """Tests to see if a cpg exists on the 3PAR array to verify cpg name

        :return: string
        """
        cpg_list = self.parser.get(section_name, 'hp3par_cpg').split(',')
        for cpg in cpg_list:
            try:
                client.getCPG(cpg.strip())
            except (hpexceptions.HTTPNotFound, configparser.NoOptionError):
                return "fail"
        return "pass"

    def iscsi_is_valid(self, section_name, client):
        """Gets the iSCSI target ports from the client, checks the iSCSI IPs.

        :return: string
        """
        valid_ips = []
        try:
            ip_list = self.parser.get(section_name, 'hp3par_iscsi_ips').split(
                ",")
        except configparser.NoOptionError:
            return "fail"
        for port in client.getPorts()['members']:
            if (port['mode'] == client.PORT_MODE_TARGET and
                    port['linkState'] == client.PORT_STATE_READY and
                    port['protocol'] == client.PORT_PROTO_ISCSI):
                valid_ips.append(port['IPAddr'])
        for ip_addr in ip_list:
            ip = ip_addr.strip().split(':')
            if ip[0] not in valid_ips:
                return "fail"
        return "pass"

    def has_driver(self, section_name):
        """Checks that the volume_driver is installed

        :return: string
        """
        path = self.parser.get(section_name, 'volume_driver').split(
            '.')[-2]
        response = self.ssh_client.execute('locate ' + path)
        if path in response:
            return "pass"
        elif 'command not found' or 'command-not-found' in response:
            logger.warning("Could not check %s driver on node %s. Make sure "
                           "that 'mlocate' is installed on the node." %
                           (section_name, self.node))
            return "unknown"
        else:
            return "fail"

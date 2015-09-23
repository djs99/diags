#  (c) Copyright 2015 Hewlett Packard Enterprise Development LP
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
This checks the cinder.conf file to find errors in the configuration of 3PAR
arrays.

Requires the python hp3parclient: sudo pip install hp3parclient
Assumes the volume_driver is correctly set
"""

import logging
from six.moves import configparser
from cinderdiags import constant
from cinderdiags import hp3par_testclient as testclient

logger = logging.getLogger(__name__)

try:
    from hp3parclient import client as hpclient
    from hp3parclient import exceptions as hpexceptions
except ImportError:
    logger.error('hp3parclient package not found (pip install hp3parclient)')


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
            logger.info("Checking 3PAR options for node '%s' backend section "
                         "%s" % (self.node, section_name))
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
            url = self.parser.get(section_name, 'hp3par_api_url')
            logger.info("Attempting to connect to %s..." % url)
            if test:
                cl = testclient.HP3ParClient(url)
            else:
                cl = hpclient.HP3ParClient(url)
            return cl
        except (hpexceptions.UnsupportedVersion, hpexceptions.HTTPBadRequest,
                TypeError) as e:
            logger.info("Failed to connect to hp3par_api_url for node '%s' "
                        "backend section '%s' --- %s" % (self.node,
                                                         section_name, e))
            return None
        except configparser.NoOptionError:
            logger.info("No hp3par_api_url provided for node '%s' backend "
                        "section '%s'" % (self.node, section_name))
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
                hpexceptions.HTTPUnauthorized):
            logger.info("Incorrect hp3par_username or hp3par_password "
                        "provided for node '%s' backend section '%s'" %
                        (self.node, section_name))
            return False
        except configparser.NoOptionError:
            logger.info("No hp3par_username or hp3par_password provided for "
                        "node '%s' backend section '%s'" % (self.node,
                                                            section_name))
            return False

    def cpg_is_valid(self, section_name, client):
        """Tests to see if a cpg exists on the 3PAR array to verify cpg name

        :return: string
        """
        result = "pass"
        try:
            cpg_list = [x.strip() for x in
                        self.parser.get(section_name, 'hp3par_cpg').split(',')]
            logger.info("Checking hp3par_cpg option for node '%s' backend "
                         "section '%s'" % (self.node, section_name))
            for cpg in cpg_list:
                try:
                    client.getCPG(cpg)
                except hpexceptions.HTTPNotFound:
                    logger.info("Node '%s' backend section '%s' hp3par_cpg "
                                "contains an invalid CPG name: '%s'" %
                                (self.node, section_name, cpg))
                    result = "fail"
        except configparser.NoOptionError:
            logger.info("No hp3par_cpg provided for node '%s' backend section "
                        "'%s'" %
                        (self.node, section_name))
            result = "fail"
        return result

    def iscsi_is_valid(self, section_name, client):
        """Gets the iSCSI target ports from the client, checks the iSCSI IPs.

        :return: string
        """
        valid_ips = []
        result = "pass"
        try:
            ip_list = [x.strip() for x in
                       self.parser.get(section_name,
                                       'hp3par_iscsi_ips').split(',')]
            logger.info("Checking iSCSI IP addresses for node '%s' backend "
                         "section '%s'" % (self.node, section_name))
            for port in client.getPorts()['members']:
                if (port['mode'] == client.PORT_MODE_TARGET and
                        port['linkState'] == client.PORT_STATE_READY and
                        port['protocol'] == client.PORT_PROTO_ISCSI):
                    valid_ips.append(port['IPAddr'])
            for ip_addr in ip_list:
                ip = ip_addr.split(':')
                if ip[0] not in valid_ips:
                    logger.info("Node '%s' backend section '%s' "
                                "hp3par_iscsi_ips contains an invalid iSCSI "
                                "IP '%s'" % (self.node, section_name, ip))
                    result = "fail"
        except configparser.NoOptionError:
            logger.info("No hp3par_iscsi_ips provided for node '%s' backend "
                        "section '%s" % (self.node, section_name))
            result = "fail"
        return result

    def has_driver(self, section_name):
        """Checks that the volume_driver is installed

        :return: string
        """
        try:
            volume_driver = self.parser.get(section_name, 'volume_driver')
            path = volume_driver.split('.')
            if ("%s.%s" % (path[-2], path.pop())) in constant.HP3PAR_DRIVERS:
                path = '/'.join(path)
                logger.info("Checking for driver at '%s' for node '%s' "
                             "backend section '%s'" % (self.node, path,
                                                       section_name))
                response = self.ssh_client.execute('locate ' + path)

                if path in response:
                    result = "pass"
                elif ('command not found' or 'command-not-found') in response:
                    logger.warning("Could not check '%s' driver on node'%s'. "
                                   "Make sure that 'mlocate' is installed on "
                                   "the node." % (section_name, self.node))
                    result = "unknown"
                else:
                    logger.info("Node '%s' backend section '%s' volume_driver "
                                "contains an "
                                "invalid driver location: '%s'" % (
                        self.node, section_name,  path))
                    result = "fail"
            else:
                logger.info("Node '%s' backend section '%s' volume_driver is "
                            "invalid " % (self.node, section_name))
                result = "fail"

        except configparser.NoOptionError:
            logger.info("No volume_diver provided for node '%s' backend "
                        "section '%s'" % (self.node, section_name))
        return result

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

Requires python-3parclient: sudo pip install python-3parclient
Assumes the volume_driver is correctly set
"""

import logging
from six.moves import configparser
from cinderdiags import constant
from cinderdiags import hpe3par_testclient as testclient

logger = logging.getLogger(__name__)

try:
    from hpe3parclient import client as hpeclient
    from hpe3parclient import exceptions as hpe_exceptions
except ImportError:
    logger.error(
        'python-3parclient package not found (pip install python-3parclient)')


class WSChecker(object):

    def __init__(self, client, conf, node, test=False,
                 include_system_info=False,
                 include_replication_checks=False):
        """Tests web service api configurations in the cinder.conf file

        :param conf: location of cinder.conf
        :param node: cinder node the cinder.conf was copied from
        :param test: use testing client
        """
        self.conf = conf
        self.ssh_client = client
        self.node = node
        self.is_test = test
        self.include_system_info = include_system_info
        self.include_replication_checks = include_replication_checks
        self.parser = configparser.ConfigParser()
        self.parser.read(self.conf)
        self.hpe3pars = []
        for section in self.parser.sections():
            if self.parser.has_option(section, 'volume_driver') \
                    and 'hpe_3par' in self.parser.get(section,
                                                      'volume_driver'):
                self.hpe3pars.append(section)

    def check_all(self):
        """Tests configuration settings for all 3par arrays

        :return: a list of dictionaries
        """
        all_tests = []
        for section_name in self.hpe3pars:
            all_tests.append(self.check_section(section_name))
        return all_tests

    def check_section(self, section_name):
        logger.info("hpe3par_wsapi_checks - check_section()")
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
            "driver": "unknown",
        }
        if self.include_system_info:
            tests["system_info"] = "unknown"
            tests["conf_items"] = "unknown"

        if self.include_replication_checks:
            tests["replication_info"] = "unknown"
            tests["replication_config_items"] = "unknown"

        if section_name in self.hpe3pars:
            logger.info(
                "Checking 3PAR options for node '%s' backend section "
                "%s" % (self.node, section_name))

            if self.include_system_info:
                tests['conf_items'] = self.get_conf_items(section_name)

            if self.include_replication_checks:
                replication_config_items = \
                    self.get_replication_device_items(section_name)
                if replication_config_items:
                    tests["replication_results"] = \
                        self.verify_replication_device_info(
                            section_name,
                            replication_config_items)

            tests["driver"] = self.has_driver(section_name)
            client = self.get_client(section_name, self.is_test)
            if client:
                logger.info("client: '%s'" % (client))
                tests["url"] = "pass"
                if self.cred_is_valid(section_name, client):
                    if self.include_system_info:
                        tests["system_info"] = self.get_system_info(
                            section_name,
                            client)
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
            if 'hpe_3par_fc' in self.parser.get(section_name, 'volume_driver'):
                tests["iscsi"] = "N/A"
            return tests
        else:
            return None

# Config testing methods check if option values are valid
    def get_client(self, section_name, test, url=None):
        logger.info("hpe3par_wsapi_checks - get_client()")
        """Tries to create a client and verifies the api url

        :return: The client if url is valid, None if invalid/missing
        """
        try:
            if not url:
                url = self.parser.get(section_name, 'hpe3par_api_url')
            logger.info("Attempting to connect to %s..." % url)
            if test:
                cl = testclient.HPE3ParClient(url)
            else:
                cl = hpeclient.HPE3ParClient(url)
            return cl
        except (hpe_exceptions.UnsupportedVersion,
                hpe_exceptions.HTTPBadRequest,
                TypeError) as e:
            logger.info("Failed to connect to hpe3par_api_url for node '%s' "
                        "backend section '%s' --- %s" % (self.node,
                                                         section_name, e))
            return None
        except configparser.NoOptionError:
            logger.info("No hpe3par_api_url provided for node '%s' backend "
                        "section '%s'" % (self.node, section_name))
            return None

    def cred_is_valid(self, section_name, client, credentials=None):
        logger.info("hpe3par_wsapi_checks - cred_is_valid()")
        """Tries to login to the client to verify credentials

        :return: True if credentials are valid, False if invalid/missing
        """
        if not credentials:
            uname = self.parser.get(section_name, 'hpe3par_username')
            pwd = self.parser.get(section_name, 'hpe3par_password')
        else:
            uname = credentials['uname']
            pwd = credentials['pwd']

        logger.info("Use credentials %s -- %s: " % (uname, pwd))
        try:
            client.login(uname, pwd)
            return True
        except (hpe_exceptions.HTTPForbidden,
                hpe_exceptions.HTTPUnauthorized):
            logger.info("Incorrect hpe3par_username or hpe3par_password "
                        "provided for node '%s' backend section '%s'" %
                        (self.node, section_name))
            return False
        except configparser.NoOptionError:
            logger.info("No hpe3par_username or hpe3par_password provided for "
                        "node '%s' backend section '%s'" % (self.node,
                                                            section_name))
            return False

    def cpg_is_valid(self, section_name, client, cpg_list=None):
        logger.info("hpe3par_wsapi_checks - cpg_is_valid()")
        """Tests to see if a cpg exists on the 3PAR array to verify cpg name

        :return: string
        """
        result = "pass"
        try:
            if not cpg_list:
                cpg_list = [x.strip() for x in
                            self.parser.get(
                                section_name,
                                'hpe3par_cpg').split(',')]

            logger.info("Checking hpe3par_cpg option for node '%s' backend "
                        "section '%s'" % (self.node, section_name))
            for cpg in cpg_list:
                try:
                    logger.info("request client.getCPG(): '%s' " %
                                (cpg))
                    client.getCPG(cpg)
                except hpe_exceptions.HTTPNotFound:
                    logger.info("Node '%s' backend section '%s' hpe3par_cpg "
                                "contains an invalid CPG name: '%s'" %
                                (self.node, section_name, cpg))
                    result = "fail"
        except configparser.NoOptionError:
            logger.info("No hpe3par_cpg provided for node '%s' backend "
                        "section '%s'" %
                        (self.node, section_name))
            result = "fail"
        return result

    def iscsi_is_valid(self, section_name, client):
        logger.info("hpe3par_wsapi_checks - iscsi_is_valid()")
        """Gets the iSCSI target ports from the client, checks the iSCSI IPs.

        :return: string
        """
        valid_ips = []
        result = "pass"

        ip_list = self.get_iscsi_ips(section_name)
        if ip_list:
            logger.info("Checking iSCSI IP addresses for node '%s' backend "
                        "section '%s'" % (self.node, section_name))
            for port in client.getPorts()['members']:
                if (port['mode'] == client.PORT_MODE_TARGET and
                        port['linkState'] == client.PORT_STATE_READY and
                        port['protocol'] == client.PORT_PROTO_ISCSI):
                    valid_ips.append(port['IPAddr'])
                    logger.info(
                        "Checking iscsi IP port: '%s'" % (port['IPAddr']))
            for ip_addr in ip_list:
                ip = ip_addr.split(':')
                logger.info("ip: '%s'" % (ip))
                if ip[0] not in valid_ips:
                    logger.info("Node '%s' backend section '%s' "
                                "hpe3par_iscsi_ips or iscsi_ip_address "
                                "contains an invalid iSCSI "
                                "IP '%s'" % (self.node, section_name, ip))
                    result = "fail"

        else:
            logger.info("No hpe3par_iscsi_ips or iscsi_ip_address "
                        "provided for node '%s' backend "
                        "section '%s" % (self.node, section_name))
            result = 'fail'

        return result

    def get_iscsi_ips(self, section_name):
        ip_list = []
        try:
            # first check special HPE tag for multiple IPs
            ip_list = [x.strip() for x in
                       self.parser.get(section_name,
                                       'hpe3par_iscsi_ips').split(',')]
        except configparser.NoOptionError:
            try:
                # next check standard cinder.conf entry for single IP
                ip_addr = self.parser.get(section_name,
                                          'iscsi_ip_address')
                if ip_addr:
                    ip_list = []
                    ip_list.append(ip_addr)
                    return ip_list
            except configparser.NoOptionError:
                return None

        try:
            # next check standard cinder.conf entry for single IP
            ip_addr = self.parser.get(section_name,
                                      'iscsi_ip_address')
            if ip_addr:
                if not ip_list:
                    ip_list = []
                ip_list.append(ip_addr)
                return ip_list
        except configparser.NoOptionError:
            return ip_list

        return ip_list

    def has_driver(self, section_name):
        logger.info("hpe3par_wsapi_checks - has_driver()")
        """Checks that the volume_driver is installed

        :return: string
        """
        try:
            volume_driver = self.parser.get(section_name, 'volume_driver')
            path = volume_driver.split('.')
            logger.info("volume_driver: '%s'  path: '%s'" % (volume_driver,
                                                             path))
            if ("%s.%s" % (path[-2], path.pop())) in constant.HPE3PAR_DRIVERS:
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
                                "contains an invalid driver location: '%s'" %
                                (self.node, section_name,  path))
                    result = "fail"
            else:
                logger.info("Node '%s' backend section '%s' volume_driver is "
                            "invalid " % (self.node, section_name))
                result = "fail"

        except configparser.NoOptionError:
            logger.info("No volume_diver provided for node '%s' backend "
                        "section '%s'" % (self.node, section_name))
        return result

    def get_conf_items(self, section_name):
        logger.info("get cinder.conf items")
        """Get all items listed in config.conf for this section

        :return: string
        """
        options = ['hpe3par_api_url',
                   'hpe3par_username',
                   'hpe3par_password',
                   'hpe3par_cpg',
                   'hpe3par_iscsi_ips',
                   'iscsi_ip_address',
                   'volume_backend_name',
                   'volume_driver']

        result = ""
        for option in options:
            try:
                value = self.parser.get(section_name, option)
                logger.info("value = '%s'" % (value))
                result += option + "==" + value + ";;"
            except:
                result += option + "==<blank>" + ";;"

        result += self.format_replication_config_item_list(section_name)

        logger.info("Items: '%s'" % (result))
        return result

    def format_replication_config_item_list(self, section_name):
        # options we care about
        options = ['backend_id',
                   'replication_mode',
                   'cpg_map',
                   'hpe3par_api_url',
                   'hpe3par_username',
                   'hpe3par_password']

        format_str = ""

        entries = self.get_replication_device_items(section_name)
        for entry in entries:
            logger.info("REPLICATION config entry: '%s'" % (entry))
            if format_str:
                format_str += ";"
            format_str += ("replication_device==")
            items = entry.split("::")
            for item in items:
                format_str += (item.replace("==", "=") + ";")

        if format_str:
            format_str += ";"

        return format_str

    def get_replication_device_items(self, section_name):
        logger.info("get cinder.conf replication_device items")
        """Get all replication device items listed in config.conf for this section

        :return: string
        """

        rep_entries = []

        try:
            # can have multiple "replication_device" entries, so we need
            # to do our own parsing
            f = open(self.conf)
            in_correct_section = False
            in_replication_entry = False
            replication_lines = []
            replication_line = ''
            for line in f:
                line = line.strip()
                if "[" + section_name + "]" in line:
                    in_correct_section = True
                elif "[" in line and "]" in line:
                    in_correct_section = False

                if in_correct_section:
                    str_line = line.strip()
                    if str_line.startswith('replication_device'):
                        replication_line = line
                        if line.endswith(","):
                            in_replication_entry = True
                        else:
                            replication_lines.append(replication_line)
                    elif in_replication_entry:
                        replication_line += line
                        if not line.endswith(","):
                            in_replication_entry = False
                            replication_lines.append(replication_line)
                            logger.info("line3 = '%s'" % (replication_line))
            f.close()

            # pull out options from each "replication_device" entries
            for replicaton_line in replication_lines:
                option, value = replicaton_line.split("=", 1)
                logger.info("rep item[%s] = '%s'" % (option, value))
                value = value.strip()
                entries = value.split(",")
                rep_entry = {}
                for entry in entries:
                    if ":" in entry:
                        suboption, subvalue = entry.split(":", 1)
                        rep_entry[suboption] = subvalue
                        logger.info("rep item[%s] = '%s'" % (suboption, subvalue))
                rep_entries.append(rep_entry)

        except Exception as ex:
            logger.info("ERROR replication_device error = '%s'" % (ex))
            return None

        results = []
        for rep_entry in rep_entries:
            result = ""
            if 'backend_id' in rep_entry:
                result += "backend_id==" + rep_entry['backend_id']
            if 'replication_mode' in rep_entry:
                if result:
                    result += "::"
                result += "replication_mode==" + rep_entry['replication_mode']
            if 'cpg_map' in rep_entry:
                if result:
                    result += "::"
                result += "cpg_map==" + rep_entry['cpg_map']
            if 'hpe3par_api_url' in rep_entry:
                if result:
                    result += "::"
                result += "hpe3par_api_url==" + rep_entry['hpe3par_api_url']
            if 'hpe3par_username' in rep_entry:
                if result:
                    result += "::"
                result += "hpe3par_username==" + rep_entry['hpe3par_username']
            if 'hpe3par_password' in rep_entry:
                if result:
                    result += "::"
                result += "hpe3par_password==" + rep_entry['hpe3par_password']
            logger.info("replication entry: %s" % (result))
            results.append(result)

        return results

    def get_system_info(self, section_name, client):
        logger.info("hpe3par_wsapi_checks - get_system_info()")
        """Get all system info, including licenses

        :return: string
        """
        result = "unknown"

        try:
            info = client.getStorageSystemInfo()
            result = "name:" + info['name'] + ";;"
            result += "os_version:" + info['systemVersion'] + ";;"
            result += "model:" + info['model'] + ";;"
            result += "serial_number:" + info['serialNumber'] + ";;"
            result += "ip_address:" + info['IPv4Addr'] + ";;"
            result += "licenses:"
            if 'licenseInfo' in info:
                if 'licenses' in info['licenseInfo']:
                    valid_licenses = info['licenseInfo']['licenses']
                    one_added = False
                    for license in valid_licenses:
                        if one_added:
                            result += ";"
                        one_added = True
                        entry = license.get('name')
                        if 'expiryTimeSec' in license:
                            entry += "//" + str(license.get('expiryTimeSec'))
                        logger.info("License: '%s' - " % (entry))
                        result += entry
            info = client.getWsApiVersion()
            result += ";;wsapi_version:" + str(info['major']) + "." + \
                str(info['minor']) + "." + str(info['revision']) + \
                "." + str(info['build']) + ";;"

            # the following is needed to get pool information
            # get list of cpgs
            result += "host_name:" + self.ssh_client.get_host_name() + ";;"
            result += "backend:" + section_name + ";;"
            result += "cpgs:" + self.parser.get(section_name, 'hpe3par_cpg')

            logger.info("Result: '%s' - " % (result))
        except configparser.NoOptionError:
            logger.info("No license info for backend section "
                        "'%s'" %
                        (section_name))
        return result

    def verify_replication_device_info(self,
                                       section_name,
                                       replication_config_items):
        logger.info("hpe3par_wsapi_checks - verify_replication_device_info()")
        """Verify replcation device entries in cinder.conf

        :return: string
        """
        result_str = ""

        for config_items in replication_config_items:
            result = {
                # "overall": "pass",
                "backend_id": "Unknown",
                "wsapi": "fail",
                "credentials": "fail",
                "source_cpgs": "fail",
                "destination_cpgs": "fail",
                "replication_mode": "fail",
            }
            items = config_items.split("::")

            id = self.find_replication_option(items, "backend_id")
            if id:
                result['backend_id'] = id

            replication_mode = self.find_replication_option(items,
                                                            "replication_mode")
            if replication_mode == 'periodic' or replication_mode == "sync":
                result['replication_mode'] = "pass"

            api_url = self.find_replication_option(items, "hpe3par_api_url")
            if api_url:
                client = self.get_client(section_name, False, api_url)
                if client:
                    result['wsapi'] = "pass"
                    credentials = {
                        'uname': self.find_replication_option(
                            items,
                            "hpe3par_username"),
                        'pwd': self.find_replication_option(
                            items,
                            "hpe3par_password"),
                    }
                    if self.cred_is_valid(section_name, client, credentials):
                        result["credentials"] = "pass"

                        # for cpgs, they are provide in a format that is:
                        # fromCPG1:toCPG1 fromCPG2:fromCPG2
                        # verify fromCPGs by simply checking if they are
                        # listed hpe3par_cpg
                        # verify toCPGs by checking if they exist on
                        # replication device
                        from_cpg_list = self.get_replication_cpgs(items)
                        result['source_cpgs'] = \
                            self.verify_replication_source_cpgs(section_name,
                                                                from_cpg_list)

                        to_cpg_list = self.get_replication_cpgs(
                            items,
                            on_replication_device=True)
                        result['desctination_cpgs'] = \
                            self.cpg_is_valid(section_name,
                                              client,
                                              to_cpg_list)

            result_str += \
                "Backend ID:" + result['backend_id'] + ";;" + \
                " WS API:" + result['wsapi'] + ";;" + \
                " Credentials:" + result['credentials'] + ";;" + \
                " Source CPGs:" + result['source_cpgs'] + ";;" + \
                " Destination CPGs:" + result['destination_cpgs'] + ";;" + \
                " Replication Mode:" + result['replication_mode'] + ";;"

        logger.info("Replication Verification Result: '%s'" % (result_str))
        return result_str

    def find_replication_option(self, items, option):
        for item in items:
            entry = item.split("==")
            if entry[0] == option:
                return entry[1]

        return None

    def get_replication_cpgs(self, items, on_replication_device=False):
        cpg_list = []
        cpg_map = self.find_replication_option(items, "cpg_map")
        cpg_pairs = cpg_map.split(" ")
        for cpg_pair in cpg_pairs:
            cpgs = cpg_pair.split(":")
            if on_replication_device:
                # cpgs on replication device are listed second
                cpg_list.append(cpgs[1])
            else:
                cpg_list.append(cpgs[0])

        return cpg_list

    def verify_replication_source_cpgs(self, section_name, from_cpg_list):
        # get source cpg list from cinder.conf
        cpg_list = \
            [x.strip() for x in self.parser.get(section_name,
                                                'hpe3par_cpg').split(',')]

        # verify each of the from_cpg_list cpgs is listed in main
        # cinder.conf cpg list
        result = "pass"

        for cpg in from_cpg_list:
            if cpg not in cpg_list:
                logger.info("No match for replication cpg: '%s'" % (cpg))
                return "fail"

        return result

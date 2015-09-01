"""
Reads cli.conf & does the things
"""

import ConfigParser
import wsapi_conf
import ssh_client
import pkg_checks
import constant
import os
import logging
from pkg_resources import resource_filename



logger = logging.getLogger(__name__)


parser = ConfigParser.SafeConfigParser()


class Reader(object):

    def __init__(self, is_test=False):
        self.is_test = is_test
        self.cinder_nodes = []
        self.cinder_files = {}
        self.nova_nodes = []

        parser.read(resource_filename('cinderdiags', constant.CLI_CONFIG))
        # parser.read(constant.CLI_CONFIG)
        if self.is_test:
            self.test_parse()
        else:
            self.real_parse()

    def test_parse(self):
        """
        When test flag is set, only parse sections with 'service=test' add
        them all to both cinder and nova lists
        """
        for section_name in list(parser.sections()):
            if parser.get(section_name, 'service').lower() == 'test':
                self.cinder_nodes.append(section_name)
                self.nova_nodes.append(section_name)

    def real_parse(self):
        """
        Create lists of cinder and nova nodes
        """
        for section_name in list(parser.sections()):
            if parser.get(section_name, 'service').lower() == 'cinder':
                self.cinder_nodes.append(section_name)
            elif parser.get(section_name, 'service').lower() == 'nova':
                self.nova_nodes.append(section_name)

    def copy_files(self):
        """
        Copy the cinder.conf file of each cinder node to a local directory.
        Location of cinder.conf file is set per node in cli.conf
        """
        for node in self.cinder_nodes:
            client = ssh_client.Client(parser.get(node, 'host_ip'),
                                       parser.get(node, 'ssh_user'),
                                       parser.get(node, 'ssh_password')
                                       )
            f = client.get_file(parser.get(node, 'conf_source'),
                                node + constant.EXTENSION)
            if f:
                self.cinder_files[node] = f
            else:
                logger.warning("%s ignored" % node)

            client.disconnect()

    def pkg_checks(self, name='default', service='default', version=None):
        """
        Check nodes for installed software packages
        :param name: Name of a software package to check for
        :param service: cinder or nova
        :param version: minimum version of software package
        :return: list of dictionaries
        """
        if service == 'nova':
            checklist = self.nova_nodes
        elif service == 'cinder':
            checklist = self.cinder_nodes
        else:
            checklist = set(self.nova_nodes + self.cinder_nodes)
        checks = []
        for node in checklist:
            client = ssh_client.Client(parser.get(node, 'host_ip'),
                                       parser.get(node, 'ssh_user'),
                                       parser.get(node, 'ssh_password')
                                       )
            if name == 'default':
                checks += pkg_checks.check_all(client, node, (parser.get(
                    node, 'service').lower(), 'default'))

            else:
                checks.append(pkg_checks.check_package(client, node,
                                                       (name, version)))
            client.disconnect()
        return checks

    def ws_checks(self, section_name='arrays'):
        """
        Check WS API options set in each cinder.conf file copied from the
        cinder nodes.
        :param section_name: section name in the cinder.conf file.  Checks
        all by default
        :return: list of dictionaries
        """
        checks = []
        for node in self.cinder_files:
            checker = wsapi_conf.WSChecker(self.cinder_files[node], node,
                                           self.is_test)
            if section_name == 'arrays':
                checks += checker.check_all()
            else:
                found = checker.check_section(section_name)
                if found:
                    checks.append(found)
        return checks

    def cleanup(self):
        """
        Delete all copied cinder.conf files
        """
        for node in self.cinder_files:
            os.remove(self.cinder_files[node])

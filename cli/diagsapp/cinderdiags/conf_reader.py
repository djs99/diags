from __future__ import absolute_import
import logging
import os

from . import constant
from . import pkg_checks
from . import ssh_client
from . import wsapi_conf

from pkg_resources import resource_filename
from six.moves import configparser

# ConfigParser.SafeConfigParser() became configparser.ConfigParser()
# if sys.version_info < (3, 2):
#     import ConfigParser
#     parser = ConfigParser.SafeConfigParser()
# else:
#     import configparser
#     parser = configparser.ConfigParser()


logger = logging.getLogger(__name__)
parser = configparser.ConfigParser()

class Reader(object):

    def __init__(self, is_test=False):
        self.is_test = is_test
        self.cinder_nodes = []
        self.nova_nodes = []
        self.cinder_files = {}
        self.clients = {}
        parser.read(resource_filename('cinderdiags', constant.CLI_CONFIG))
        if self.is_test:
            self.test_parse()
        else:
            self.real_parse()
        self.get_clients()
        if len(self.cinder_nodes) < 1:
            logger.warning("No Cinder nodes are configured in cli.conf")
        if len(self.nova_nodes) < 1:
            logger.warning("No Nova nodes are configured in cli.conf")

    def test_parse(self):
        """Only parse sections with 'service=test' add to cinder and nova lists
        """
        for section_name in list(parser.sections()):
            if parser.get(section_name, 'service').lower() == 'test':
                self.cinder_nodes.append(section_name)
                self.nova_nodes.append(section_name)

    def real_parse(self):
        """Create lists of cinder and nova nodes
        """
        for section_name in list(parser.sections()):
            if parser.get(section_name, 'service').lower() == 'cinder':
                self.cinder_nodes.append(section_name)
            elif parser.get(section_name, 'service').lower() == 'nova':
                self.nova_nodes.append(section_name)

    def get_clients(self):
        """Create SSH client connections for nodes.
        """
        for node in set(self.nova_nodes + self.cinder_nodes):
            try:
                client = ssh_client.Client(parser.get(node, 'host_ip'),
                                           parser.get(node, 'ssh_user'),
                                           parser.get(node, 'ssh_password'))
                self.clients[node] = client
            except Exception as e:
                logger.warning("%s: %s" % (e, node))

    def copy_files(self):
        """Copy the cinder.conf file of each cinder node to a local directory.

        Location of cinder.conf file is set per node in cli.conf
        """
        for node in self.cinder_nodes:
            try:
                conf_file = self.clients[node].get_file(parser.get(
                    node, 'conf_source'), constant.DIRECTORY + node)
                self.cinder_files[node] = conf_file
            except Exception as e:
                logger.warning("%s: %s" % (e, node))

    def pkg_checks(self, name='default', service='default', version=None):
        """Check nodes for installed software packages

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
            if name == 'default':
                checks += pkg_checks.check_all(self.clients[node], node,
                                               (parser.get(node,
                                                           'service').lower(
                                               ), 'default'))
            else:
                checks.append(pkg_checks.dpkg_check(self.clients[node],
                                                    node, (name, version)))
        return checks

    def ws_checks(self, section_name='arrays'):
        """Check WS API options in each cinder.conf file

        :param section_name: section name in the cinder.conf file.  Checks
        all by default
        :return: list of dictionaries
        """
        checks = []
        for node in self.cinder_files:
            checker = wsapi_conf.WSChecker(self.clients[node],
                                           self.cinder_files[node],
                                           node,
                                           self.is_test)
            if section_name == 'arrays':
                checks += checker.check_all()
            else:
                found = checker.check_section(section_name)
                if found:
                    checks.append(found)
        return checks

    def cleanup(self):
        """Delete all copied cinder.conf files and close all SSH connections.
        """
        for node in self.cinder_files:
            os.remove(self.cinder_files[node])
        for node in self.clients:
            self.clients[node].disconnect()

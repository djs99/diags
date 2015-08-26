"""
Reads cli.conf & does the things
"""

import ConfigParser
import wsapi_conf
import ssh_client
import pkg_checks

PREFIX = 'config/'
SUFFIX = '.tmp'
parser = ConfigParser.SafeConfigParser()


class Reader(object):

    def __init__(self, is_test=False):
        self.is_test = is_test
        self.cinder_nodes = []
        self.nova_nodes = []

        parser.read('cinderdiags/cli.conf')
        if self.is_test:
            self.test_parse()
        else:
            self.real_parse()

    def test_parse(self):
        for section_name in list(parser.sections()):
            if parser.get(section_name, 'service').lower() == 'test':
                self.cinder_nodes.append(section_name)
                self.nova_nodes.append(section_name)

    def real_parse(self):
        for section_name in list(parser.sections()):
            if parser.get(section_name, 'service').lower() == 'cinder':
                self.cinder_nodes.append(section_name)
            elif parser.get(section_name, 'service').lower() == 'nova':
                self.nova_nodes.append(section_name)

    def copy_files(self):
        for node in self.cinder_nodes:
            client = ssh_client.Client(parser.get(node, 'host_ip'),
                                       parser.get(node, 'ssh_user'),
                                       parser.get(node, 'ssh_password')
                                       )
            client.get_file(parser.get(node, 'conf_source'), PREFIX + node + SUFFIX)
            client.disconnect()

    def pkg_checks(self, name, service='default', version=None):
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

                checks.append(pkg_checks.check_package(client, node, (name,
                                                                      version)))
            client.disconnect()
        return checks

    def ws_checks(self, section_name='arrays'):
        checks = []
        for node in self.cinder_nodes:
            checker = wsapi_conf.WSChecker(PREFIX + node + SUFFIX, node,
                                           self.is_test)
            if section_name == 'arrays':
                checks += checker.check_all()
            else:
                found = checker.check_section(section_name)
                if found:
                    checks.append(found)
        return checks

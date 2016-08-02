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
import json
import logging
import os

from cinderdiags import constant
from cinderdiags import pkg_checks
from cinderdiags import lun_stats
from cinderdiags import ssh_client
from cinderdiags import hpe3par_wsapi_checks as wsapi_checks

from six.moves import configparser


logger = logging.getLogger(__name__)
parser = configparser.ConfigParser()


class Reader(object):

    arg_data = None

    def __init__(self, is_test=False, path=None, json_data=None, get_info=False):
        self.is_test = is_test
        self.include_system_info = get_info
        self.cinder_nodes = []
        self.nova_nodes = []

        if json_data:
            self.arg_data = json.loads(json_data)
            logger.warning("DATA: %s" % (self.arg_data))

            for section in self.arg_data:
                if section['service'].lower() == 'cinder':
                    self.cinder_nodes.append(section['section'])
                elif section['service'].lower() == 'nova':
                    self.nova_nodes.append(section['section'])
        else:
            if self.is_test:
                path = constant.TEST_CLI_CONFIG
            elif path is None:
                path = constant.CLI_CONFIG
            if os.path.isfile(path):
                parser.read(path)
                self.get_nodes()
                if len(self.cinder_nodes) < 1:
                    logger.warning("No Cinder nodes are configured in cli.conf")
                if len(self.nova_nodes) < 1:
                    logger.warning("No Nova nodes are configured in cli.conf")
            else:
                raise IOError("%s path not found" % path)

    def get_nodes(self):
        """Create lists of cinder and nova nodes
        """
        for section_name in list(parser.sections()):
            if parser.get(section_name, 'service').lower() == 'cinder':
                self.cinder_nodes.append(section_name)
            elif parser.get(section_name, 'service').lower() == 'nova':
                self.nova_nodes.append(section_name)

    def get_clients(self, nodes):
        """Create SSH client connections for nodes.
        """
        clients = {}

        for node in nodes:
            logger.warning("PROCESS NODE: %s" % (node))
            try:
                if self.arg_data:
                    for section in self.arg_data:
                        if section['section'].lower() == node:
                            logger.warning("Found section: %s" % (node))
                            logger.warning("Attempt to open SSH connection to: %s"
                                           % (section['host_ip']))
                            client = ssh_client.Client(section['host_ip'],
                                                       section['ssh_user'],
                                                       section['ssh_password'])
                            logger.warning("Opened SSH connection")
                else:
                    client = ssh_client.Client(parser.get(node, 'host_ip'),
                                               parser.get(node, 'ssh_user'),
                                               parser.get(node, 'ssh_password'))
                clients[node] = client
            except Exception as e:
                logger.warning("%s: %s" % (e, node))
                pass
        return clients

    def copy_files(self, clients):
        """Copy the cinder.conf file of each cinder node to a local directory.

        Location of cinder.conf file is set per node in cli.conf
        """
        files = {}
        for node in self.cinder_nodes:
            try:
                conf_file_name = None
                if self.arg_data:
                    for section in self.arg_data:
                        if section['section'].lower() == node:
                            conf_file_name = section['conf_source']
                else:
                    conf_file_name = parser.get(node, 'conf_source')

                logger.warning("Conf file name: %s" % (conf_file_name))
                conf_file = clients[node].get_file(conf_file_name,
                                                   constant.DIRECTORY + node)
                files[node] = conf_file
            except Exception as e:
                logger.warning("%s: %s" % (e, node))
        return files

    def software_check(self, name='default', service='default',
                       version=None, packages=None):
        """Check nodes for installed software packages

        :param name: Name of a software package to check for
        :param service: cinder or nova
        :param version: minimum version of software package
        :param packages: alternate JSON structure to pass in multiple packages
        :return: list of dictionaries
        """
        if service == 'nova':
            checklist = self.nova_nodes
        elif service == 'cinder':
            checklist = self.cinder_nodes
        else:
            checklist = set(self.nova_nodes + self.cinder_nodes)
        clients = self.get_clients(checklist)

        checks = []
        for node in checklist:
            try:
                if packages:
                    pkg_data_list = json.loads(packages)
                    logger.warning("Software Packages: %s" % (pkg_data_list))
                    for pkg_data in pkg_data_list:
                        for pkg_name, pkg_version in pkg_data.iteritems():
                            checks.append(pkg_checks.check_one(clients[node],
                                                               node,
                                                               (pkg_name,
                                                                pkg_version)))
                elif name == 'default':
                    service = None
                    if self.arg_data:
                        for section in self.arg_data:
                            if section['section'].lower() == node:
                                service = section['service']
                    else:
                        service = parser.get(node, 'service')

                    checks += pkg_checks.check_all(clients[node],
                                                   node,
                                                   service)
                else:
                    checks.append(pkg_checks.check_one(clients[node],
                                                       node,
                                                       (name, version)))
            except Exception as e:
                logger.warning("%s: %s" % (e, node))
        self.cleanup(clients)
        return checks

    def options_check(self, section_name='arrays'):
        """Check WS API options in each cinder.conf file

        :param section_name: section name in the cinder.conf file.  Checks
        all by default
        :return: list of dictionaries
        """
        clients = self.get_clients(self.cinder_nodes)
        files = self.copy_files(clients)
        checks = []
        for node in files:
            checker = wsapi_checks.WSChecker(clients[node],
                                             files[node],
                                             node,
                                             self.is_test,
                                             self.include_system_info)
            if section_name == 'arrays':
                checks += checker.check_all()
            else:
                found = checker.check_section(section_name)
                if found:
                    checks.append(found)
        self.cleanup(clients, files)
        return checks

    def credentials_check(self):
        """Validate SSH credentials
        """
        logger.warning("Check SSH credentials")
        checklist = set(self.nova_nodes + self.cinder_nodes)
        clients = self.get_clients(checklist)

        checks = []
        for node in checklist:
            # clients only exist for nodes that SSH connect was successful
            logger.warning("Check credentials for node: %s" % (node))
            if node in clients:
                result = 'pass'
            else:
                result = 'fail'
            logger.warning("Credentials result: %s" % (result))
            checks.append({'node': node,
                           'connect': result })

        self.cleanup(clients)
        return checks

    def volume_paths_check(self, os_vars, attached_volumes=None):
        """Check nodes for installed software packages

        :param attached_volumes: a JSON structure
        :return: list of dictionaries
        """
        checklist = self.nova_nodes
        clients = self.get_clients(checklist)

        paths = []
        for node in checklist:
            try:
                paths = lun_stats.get_all_paths(clients[node], node, os_vars)
                if attached_volumes:
                    volume_list = json.loads(attached_volumes)
                    logger.info("Volumes List: %s" % (volume_list))
                    for volume in volume_list:
                        vol_paths = lun_stats.get_paths_for_volume(
                            clients[node],
                            node,
                            volume)
                        for vol_path in vol_paths:
                            for cur_path in paths:
                                if cur_path['path'] == vol_path:
                                    cur_path['vol_name'] = volume
                                    break

            except Exception as e:
                logger.warning("%s: %s" % (e, node))
        self.cleanup(clients)
        return paths

    def cleanup(self, clients, files={}):
        """Delete all copied cinder.conf files and close all SSH connections.
        """
        for node in clients:
            clients[node].disconnect()
        for node in files:
            os.remove(files[node])

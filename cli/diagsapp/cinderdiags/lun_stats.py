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

from cinderdiags import constant

logger = logging.getLogger(__name__)

def get_all_paths(client, node, json_os_vars):
    """Check for packages installed via apt-get (Debian Linux)

    :param client: ssh client
    :param node: node being checked
    :param os_vars: OpenStack env variables required to run Cinder commands
    :return: dictionary list
    """

    paths = []
    try:
        os_vars = json.loads(json_os_vars)
        logger.info("Requesting all volume paths using OpenStack vars %s" % (os_vars))

        export_cmd = "export OS_USERNAME=%s; " \
                     "export OS_PASSWORD=%s; " \
                     "export OS_TENANT_NAME=%s; " \
                     "export OS_AUTH_URL=%s;" % (os_vars['os_username'],
                                                 os_vars['os_password'],
                                                 os_vars['os_tenant'],
                                                 os_vars['os_auth'])

        logger.info("export_cmd %s" % (export_cmd))
        resp = client.execute(export_cmd +
                              " sudo cinder get-all-volume-paths --protocol 'ISCSI'")
        iscsi_paths = resp.strip().split()
        resp = client.execute(export_cmd +
                              " sudo cinder get-all-volume-paths --protocol 'FIBRE_CHANNEL'")
        fc_paths = resp.strip().split()

        for iscsi_path in iscsi_paths:
            if "-iscsi-" in iscsi_path:
                path_entry = {}
                path_entry['path'] = iscsi_path
                path_entry['vol_name'] = None
                paths.append(path_entry)
        for fc_path in fc_paths:
            if "-fc-" in fc_path:
                path_entry = {}
                path_entry['path'] = fc_path
                path_entry['vol_name'] = None
                paths.append(path_entry)

        logger.info("PATHS [%s]: %s" % (len(paths), paths))
    except Exception as e:
        logger.warning("%s -- Unable to get volume paths on node %s" % (e,
                                                                        node))
        pass
    return paths

def get_paths_for_volume(client, node, volume):
    """Check for packages installed via apt-get (Debian Linux)

    :param client: ssh client
    :param node: node being checked
    :param volume: name or ID of volume
    :return: dictionary list
    """

    paths = []
    try:
        logger.info("Requesting volume paths on node %s for volume %s" % (node, volume))
        export_cmd = "export OS_USERNAME=admin; export OS_PASSWORD=hpinvent; " \
                     "export OS_TENANT_NAME=admin; export OS_AUTH_URL=http://localhost:35357;"
        resp = client.execute(export_cmd +
                              " sudo cinder get-volume-paths " + volume)
        paths = resp.strip().split()

        logger.info("PATHS [%s]: %s" % (len(paths), paths))
    except Exception as e:
        logger.warning("%s -- Unable to get volume paths for volume %s on node %s" %
                       (e, volume, node))
        pass
    return paths

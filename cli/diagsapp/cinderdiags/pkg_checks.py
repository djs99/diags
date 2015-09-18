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

import logging
import re
from cinderdiags import constant


logger = logging.getLogger(__name__)


def check_all(client, node, service):
    """Check for default packages on cinder or nova node

    :param client: ssh client
    :param node: node being checked
    :param pkg_info: tuple of ('package name', 'minimum version')
    :return: list of dictionaries
    """
    defaults = {
        'cinder': constant.CINDER_PACKAGES,
        'nova': constant.NOVA_PACKAGES,
    }

    checked = []
    checker = get_check_type(client, node)
    if checker is not None:
        for pkg in defaults[service]:
            check = checker(client, node, pkg)
            if check['installed'] == 'unknown':
                check = pip_check(client, node, pkg)
            checked.append(check)
    else:
        checked.append({
            'node': node,
            'name': 'ERROR',
            'installed': 'ERROR',
            'version': 'ERROR',
        })
    return checked


def check_one(client, node, pkg_info):
    """Check for a single package on a single node

    :param client: ssh client
    :param node: node being checked
    :param pkg_info: tuple of ('package name', 'minimum version')
    :return: dictionary
    """

    checker = get_check_type(client, node)
    if checker is not None:
        check = checker(client, node, pkg_info)
        if check['installed'] == 'unknown':
            check = pip_check(client, node, pkg_info)
    else:
        check = {
            'node': node,
            'name': pkg_info[0],
            'installed': 'ERROR',
            'version': 'ERROR',
        }
    return check


def dpkg_check(client, node, pkg_info):
    """Check for packages installed via apt-get (Debian Linux)

    :param client: ssh client
    :param node: node being checked
    :param pkg_info: (name, version)
    :return: dictionary
    """
    pkg = {
        'node': node,
        'name': pkg_info[0],
        'installed': 'unknown',
        'version': 'N/A',
    }

    names = [x.strip() for x in pkg_info[0].split('||')]
    try:
        for name in names:
            logger.info("Checking for software package '%s' on node %s using "
                        "dpkg-query" % (name, node))
            response = client.execute("dpkg-query -W -f='${Status}"
                                      "${Version}' " + name)
            if 'install ok installed' in response:
                pkg['installed'] = 'pass'
                pkg['name'] = name
                if pkg_info[1]:
                    pattern = re.compile('\D([\d\.]+\d)\D')
                    pkg['version'] = version_check(response,
                                                   pattern,
                                                   pkg_info[1])
                break

    except Exception as e:
        logger.warning("%s -- Unable to check %s on node %s" % (e,
                                                                pkg['name'],
                                                                node))
        pkg['installed'] = 'ERROR'
        pkg['version'] = 'ERROR'
        pass
    return pkg


def yum_check(client, node, pkg_info):
    """Check for packages installed via yum (RedHat Linux)

    :param client: ssh client
    :param node: node being checked
    :param pkg_info: (name, version)
    :return: dictionary
    """
    pkg = {
        'node': node,
        'name': pkg_info[0],
        'installed': 'unknown',
        'version': 'N/A',
    }

    names = [x.strip() for x in pkg_info[0].split('||')]
    try:
        for name in names:
            logger.info("Checking for software package '%s' on node %s using "
                        "yum" % (name, node))
            response = client.execute("yum list installed " +
                                      name)
            if 'Available Packages' in response:
                pkg['installed'] = 'fail'
                pkg['name'] = name
            elif 'Installed Packages' in response:
                pkg['installed'] = 'pass'
                pkg['name'] = name
                if pkg_info[1]:
                    pattern = re.compile(name + '\.[\w+]+\D*([\d\.]+\d)\D')
                    pkg['version'] = version_check(response,
                                                   pattern,
                                                   pkg_info[1])
                break

    except Exception as e:
        logger.warning("%s -- Unable to check %s on node %s" % (e,
                                                                pkg['name'],
                                                                node))
        pkg['installed'] = 'ERROR'
        pkg['version'] = 'ERROR'
        pass
    return pkg


def zypper_check(client, node, pkg_info):
    """Check for packages installed via zypper (SUSE Linux)

    :param client: ssh client
    :param node: node being checked
    :param pkg_info: (name, version)
    :return: dictionary
    """
    pkg = {
        'node': node,
        'name': pkg_info[0],
        'installed': 'unknown',
        'version': 'N/A',
    }

    names = [x.strip() for x in pkg_info[0].split('||')]

    try:
        for name in names:
            logger.info("Checking for software package '%s' on node %s using "
                        "zypper" % (name, node))
            response = client.execute("zypper info " +
                                      name)
            if 'Installed: No' in response:
                pkg['installed'] = 'fail'
                pkg['name'] = name
            elif 'Installed: Yes' in response:
                pkg['installed'] = 'pass'
                pkg['name'] = name
                if pkg_info[1]:
                    pattern = re.compile('Version: \D*([\d\.]+\d)\D')
                    pkg['version'] = version_check(response,
                                                   pattern,
                                                   pkg_info[1])
                break

    except Exception as e:
        logger.warning("%s -- Unable to check %s on node %s" % (e,
                                                                pkg['name'],
                                                                node))
        pkg['installed'] = 'ERROR'
        pkg['version'] = 'ERROR'
        pass
    return pkg


def pip_check(client, node, pkg_info):
    """Check for packages installed via pip (pypi packages)

    :param client: ssh client
    :param node: node being checked
    :param pkg_info: (name, version)
    :return: dictionary
    """
    pkg = {
        'node': node,
        'name': pkg_info[0],
        'installed': 'unknown',
        'version': 'N/A',
    }

    names = [x.strip() for x in pkg_info[0].split('||')]
    try:
        for name in names:
            logger.info("Checking for software package '%s' on node %s using "
                        "pip" % (name, node))
            response = client.execute("pip list | grep " + name)
            if response and re.match(name + '\s', response):
                pkg['installed'] = 'pass'
                pkg['name'] = name
                if pkg_info[1]:
                    pattern = re.compile('\(([\d\.]+)\)')
                    pkg['version'] = version_check(response,
                                                   pattern,
                                                   pkg_info[1])
                break
        if pkg['installed'] == 'unknown':
            pkg['installed'] = "fail"
    except Exception as e:
        logger.warning("%s -- Unable to check %s on node %s" % (e,
                                                                pkg['name'],
                                                                node))
        pkg['installed'] = 'ERROR'
        pkg['version'] = 'ERROR'
    return pkg


def version_check(response, pattern, min_v):
    version = pattern.search(response)
    if version is None:
        return 'unknown'
    elif version.group(1) >= min_v:
        return 'pass'
    else:
        return 'fail'


def get_check_type(client, node):
    """Checks the Linux OS flavor and returns the correct check type

    :param client: ssh client
    :param node: node being checked
    :return: function that expects parameters (client, node, pkg_info)
    """
    os_names = {
        "debian": dpkg_check,
        "fedora": yum_check,
        "suse": zypper_check,
    }
    check_type = None
    response = client.execute('cat /etc/*release | grep ^ID_LIKE')
    for os, check in list(os_names.items()):
        if re.compile(os).search(response):
            logger.info("Detected %s operating system on node %s" % (os, node))
            check_type = check
    if check_type is None:
        logger.error("Unable to determine operating system on %s" % node)
    return check_type

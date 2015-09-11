from __future__ import absolute_import
import logging
import re
from . import constant


logger = logging.getLogger(__name__)


def check_all(client, node, pkg_info):
    """Check for installed packages on the nova node

    :param client: ssh client
    :param node: node being checked
    :param pkg_info: tuple of ('package name', 'minimum version')
    :return: list of dictionaries
    """

    os_names = {
        "debian": dpkg_check,
        "rhel fedora": yum_check,
        # "suse":, zypper_check),
    }

    default_nova = constant.NOVA_PACKAGES
    default_cinder = constant.CINDER_PACKAGES

    check_type = None
    checked = []
    # Determine Linux flavor to determine package check command
    response = client.execute('cat /etc/*release | grep ^ID_LIKE') # can
    # this be done by sys call?
    for os, check in os_names.items():
        if re.compile(os).search(response):
            check_type = check
    if check_type is None:
        raise Exception("Unable to determine operating system")

    if pkg_info[0] in ['nova', 'test']:
        for pkg in default_nova:
            checked.append(check_type(client, node, pkg))

    if pkg_info[0] in ['cinder', 'test']:
        for pkg in default_cinder:
            checked.append(pip_check(client, node, pkg))
    return checked


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
    try:
        response = client.execute("dpkg-query -W -f='${Status} ${Version}' " +
                                  pkg['name'])
        if 'install ok installed' in response:
            pkg['installed'] = 'pass'
            if pkg_info[1]:
                pattern = re.compile('installed ([\d\.]+)')
                pkg['version'] = version_check(response, pattern, pkg_info[1])
        else:
            pkg = pip_check(client, node, pkg_info)

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

    try:
        response = client.execute("yum list installed " +
                                  pkg['name'])
        if 'Available Packages' in response:
            pkg['installed'] = 'fail'

        elif 'No matching Packages' in response:
            pkg = pip_check(client, node, pkg_info)

        elif 'Installed Packages' in response:
            pkg['installed'] = 'pass'
            if pkg_info[1]:
                pattern = re.compile(pkg_info[0]+'\.[\w_]+\s+([\d\.]+)-')
                pkg['version'] = version_check(response, pattern, pkg_info[1])
        else:
            logger.warning("Unable to check %s on node %s" % (pkg['name'],
                                                              node))

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
    try:
        response = client.execute("pip list | grep " + pkg['name'])
        if response and re.match(pkg['name']+'\s', response):
            pkg['installed'] = 'pass'
            if pkg_info[1]:
                pattern = re.compile('\(([\d\.]+)\)')
                pkg['version'] = version_check(response, pattern, pkg_info[1])
        else:
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

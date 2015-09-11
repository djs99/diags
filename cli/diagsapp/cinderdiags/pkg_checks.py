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
    default_nova = constant.NOVA_PACKAGES
    default_cinder = constant.CINDER_PACKAGES

    checked = []

    if pkg_info[0] in ['nova', 'test']:
        for pkg in default_nova:
            checked.append(dpkg_check(client, node, pkg))

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
                version = re.search('installed ([\d\.]+)', response)
                if version is None:
                    pkg['version'] = 'unknown'
                elif version.group(1) >= pkg_info[1]:
                    pkg['version'] = 'pass'
                else:
                    pkg['version'] = 'fail'
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
                version = re.search('\(([\d\.]+)\)', response)
                if version is None:
                    pkg['version'] = 'unknown'
                elif version.group(1) >= pkg_info[1]:
                    pkg['version'] = 'pass'
                else:
                    pkg['version'] = 'fail'
            else:
                    pkg['version'] = 'N/A'
        else:
            pkg['installed'] = "fail"
    except Exception as e:
        logger.warning("%s -- Unable to check %s on node %s" % (e,
                                                              pkg['name'],
                                                              node))
        pkg['installed'] = 'ERROR'
        pkg['version'] = 'ERROR'
    return pkg

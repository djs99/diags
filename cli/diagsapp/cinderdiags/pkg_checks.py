import constant
import logging
import re

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
    cinder_drivers = constant.HP_DRIVERS

    checked = []

    if pkg_info[0] in ['nova', 'test']:
        for pkg in default_nova:
            checked.append(dpkg_check(client, node, pkg))

    if pkg_info[0] in ['cinder', 'test']:
        for pkg in default_cinder:
            checked.append(pip_check(client, node, pkg))
        for driver in cinder_drivers:
            checked.append(driver_check(client, node, driver))
    return checked


def dpkg_check(client, node, pkg_info):
    """Check for packages installed via apt-get

    :param client: ssh client
    :param node: node being checked
    :param pkg_info: (name, version)
    :return: dictionary
    """
    pkg = {
        'node': node,
        'name': pkg_info[0],
        'installed': 'fail',
        'version': 'N/A',
    }
    try:
        response = client.execute("dpkg-query -W -f='${Status} ${Version}' " +
                                  pkg_info[0])
        if not response:
            pkg = pip_check(client, node, pkg_info)
        elif 'install ok installed' in response:
            pkg['installed'] = 'pass'
            if pkg_info[1]:
                version = re.search('installed ([\d\.]+)', response)
                if version.group(1) >= pkg_info[1]:
                    pkg['version'] = 'pass'
                else:
                    pkg['version'] = 'fail'
        else:
            pkg['installed'] = 'fail'

    except Exception as e:
        logger.warning("%s -- Unable to check %s on node %s" % (e,
                                                              pkg['name'],
                                                              node))
        pkg['installed'] = 'ERROR'
        pkg['version'] = 'ERROR'
        pass
    return pkg


def pip_check(client, node, pkg_info):
    """Check for pypi packages

    :param client: ssh client
    :param node: node being checked
    :param pkg_info: (name, version)
    :return: dictionary
    """
    pkg = {
        'node': node,
        'name': pkg_info[0],
        'installed': 'fail',
        'version': 'N/A',
    }
    try:
        response = client.execute("pip list | grep " + pkg_info[0])
        if response:
            pkg['installed'] = 'pass'
            if pkg_info[1]:
                version = re.search('\(([\d\.]+)\)', response)
                if version.group(1) >= pkg_info[1]:
                    pkg['version'] = 'pass'
                else:
                    pkg['version'] = 'fail'
            else:
                    pkg['version'] = 'N/A'
        else:
            logger.warning("Unable to locate %s on node %s" % (pkg['name'],
                                                               node))
    except Exception as e:
        logger.warning("%s -- Unable to check %s on node %s" % (e,
                                                              pkg['name'],
                                                              node))
        pkg['installed'] = 'ERROR'
        pkg['version'] = 'ERROR'
    return pkg


def driver_check(client, node, pkg_info):
    """Look for driver path

    :param client: ssh client
    :param node: node being checked
    :param pkg_info: (name, version)
    :return: dictionary
    """
    driver = {
        'node': node,
        'name': 'Driver: ' + pkg_info[0],
        'installed': 'fail',
        'version': 'N/A',
    }
    path = client.execute("locate " + pkg_info[0])
    if path:
        driver['installed'] = 'pass'
        response = client.execute("fgrep 'VERSION =' " + path)
        if pkg_info[1] and response:
            version_resp = re.search('([\d\.]+)', response)
            if version_resp.group(1) >= pkg_info[1]:
                driver['version'] = 'pass'
            else:
                driver['version'] = 'fail'
    return driver
import re
import constant


def check_all(client, node, pkg_info):
    """
    Check for installed packages on the nova node
    :param client: ssh client
    :param pkg_info: tuple of ('package name', 'minimum version')
    :return: list of dictionaries
    """
    default_nova = constant.NOVA_PACKAGES
    default_cinder = constant.CINDER_PACKAGES

    checked = []
    if pkg_info[1] == 'default':
        if pkg_info[0] in ['nova', 'test']:
            for pkg in default_nova:
                checked.append(check_package(client, node, pkg))

        if pkg_info[0] in ['cinder', 'test']:
            for pkg in default_cinder:
                checked.append(pip_check(client, node, pkg))
    else:
        checked.append(check_package(client, node, pkg_info))
    return checked


def check_package(client, node, pkg_info):
    pkg = {'node': node,
           'name': pkg_info[0],
           'installed': 'fail',
           'version': 'fail',
           }
    response = client.execute("dpkg-query -W -f='${Status} ${Version}' " +
                              pkg_info[0])

    if response and 'install ok installed' in response:
        pkg['installed'] = 'pass'
        version = re.search('installed ([\d\.]+)', response)
        if pkg_info[1]:
            if version.group(1) >= pkg_info[1]:
                pkg['version'] = 'pass'
        else:
            pkg['version'] = 'N/A'
    elif not response:
        pip_check(client, node, pkg_info)
    return pkg


def pip_check(client, node, pkg_info):
    pkg = {'node': node,
           'name': pkg_info[0],
           'installed': 'fail',
           'version': 'fail'}
    response = client.execute("pip list | grep " + pkg_info[0])

    if response:
        pkg['installed'] = 'pass'
        version = re.search('\(([\d\.]+)\)', response)
        if pkg_info[1]:
            if version.group(1) >= pkg_info[1]:
                pkg['version'] = 'pass'
        else:
            pkg['version'] = 'N/A'
    return pkg

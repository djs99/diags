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
                checked.append(dpkg_check(client, node, pkg))

        if pkg_info[0] in ['cinder', 'test']:
            for pkg in default_cinder:
                checked.append(pip_check(client, node, pkg))
    else:
        checked.append(dpkg_check(client, node, pkg_info))
    return checked


def dpkg_check(client, node, pkg_info):
    pkg = {'node': node,
           'name': pkg_info[0],
           'installed': 'fail',
           'version': 'N/A',
           }
    response = client.execute("dpkg-query -W -f='${Status} ${Version}' " +
                              pkg_info[0])

    if response and 'install ok installed' in response:
        pkg['installed'] = 'pass'
        if pkg_info[1]:
            pkg['version'] = version_check(pkg_info[1], response)
    elif not response:
        pip_check(client, node, pkg_info)
    return pkg


def pip_check(client, node, pkg_info):
    pkg = {'node': node,
           'name': pkg_info[0],
           'installed': 'fail',
           'version': 'N/A',
           }
    response = client.execute("pip list | grep " + pkg_info[0])

    if response:
        pkg['installed'] = 'pass'
        if pkg_info[1]:
            pkg['version'] = version_check(pkg_info[1], response)
    else:
        driver_check(client,node,pkg_info)
    return pkg


def driver_check(client, node, pkg_info):
    driver = {'node': node,
              'name': pkg_info[0],
              'installed': 'fail',
              'version': 'N/A',
              }
    path = client.execute("locate " + pkg_info[0])
    if path:
        driver['installed'] = 'pass'
        response = client.execute("fgrep 'VERSION =' " + path)
        if pkg_info[1]:
            driver['version'] = version_check(pkg_info[1], response)


def version_check(min_v, response):
    version = re.search('([\d\.]+)', response)
    if version.group(1) >= min_v:
        return 'pass'
    else:
        return 'fail'


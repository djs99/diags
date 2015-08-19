import sshClient
import re


def nova_check(ip, user, pswd, pkg_info=('default', 'default')):
    """
    Check for installed packages on the nova node
    :param ip: address of nova node
    :param user: ssh username
    :param pswd: ssh password
    :param pkg_info: tuple of ('package name', 'minimum version')
    :return: list of dictionaries
    """
    packages = [('sysfsutils',  '2.1'),
                ('sg3-utils', '1.3'),
                ]
    checked = []
    client = sshClient.Client(ip, user, pswd)
    if pkg_info[0] == 'default':
        for pkg in packages:
            checked.append(package_check(client, pkg))
    else:
        checked.append(package_check(client, pkg_info))
    client.disconnect()
    return checked


def package_check(client, pkg_info):
    pkg = {'name': pkg_info[0]}
    response = client.execute("dpkg-query -W -f='${Status} ${Version}' " +
                              pkg_info[0])
    if 'install ok installed' in response:
        pkg['installed'] = 'pass'
        version = re.search('([\d\.]+)', response)
        if version.group(0) >= pkg_info[1]:
            pkg['version'] = 'pass'
        else:
            pkg['version'] = 'fail'
    else:
            pkg['installed'] = 'fail'
    return pkg

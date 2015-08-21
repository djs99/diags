import re


def check_all(client):
    """
    Check for installed packages on the nova node
    :param client: ssh client
    :param pkg_info: tuple of ('package name', 'minimum version')
    :return: list of dictionaries
    """
    packages = [('sysfsutils',  '2.1'),
                ('sg3-utils', '1.3'),
                ]
    checked = []
    for pkg in packages:
        checked.append(check_package(client, pkg))
    return checked


def check_package(client, pkg_info):
    pkg = {'name': pkg_info[0],
           'installed': 'fail',
           'version': 'fail',
           }
    response = client.execute("dpkg-query -W -f='${Status} ${Version}' " +
                              pkg_info[0])
    if 'install ok installed' in response:
        pkg['installed'] = 'pass'
        version = re.search('([\d\.]+)', response)
        if version.group(0) >= pkg_info[1]:
            pkg['version'] = 'pass'
    return pkg

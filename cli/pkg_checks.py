import sshClient
import re


def nova_check(ip, user, pswd):
    packages = [{'name': 'sysfsutils', 'min_version': '2.1'},
                {'name': 'sg3-utils', 'min_version': '1.3'},
    ]
    client = sshClient.Client(ip, user, pswd)
    for pkg in packages:
        response = client.execute("dpkg-query -W -f='${Status} ${Version}' " +
                                  pkg['name'])
        if 'install ok installed' in response:
            pkg['installed'] = 'pass'
            version = re.search('([\d\.]+)', response)
            if version.group(0) >= pkg['min_version']:
                pkg['version'] = 'pass'
            else:
                pkg['version'] = 'fail'
        else:
            pkg['installed'] = 'fail'
    client.disconnect()
    return packages

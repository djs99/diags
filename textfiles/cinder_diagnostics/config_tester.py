"""
This checks the cinder.conf file to find errors in the configuration of 3PAR
arrays.

Requires the python hp3parclient: sudo pip install hp3parclient
Assumes the volume_driver is correctly set
"""
import ConfigParser

# Stupid stupidness just to test this because I don't understand the package
#  management at all
# hp3parclient.client requires Crypto, which is in /usr/lib/python2.7
#  Somehow this isn't an issue when Cinder uses hp3parclient, but it is an
# issue when I try to import it because everything is awful and
# python is the devil and vagrant was built by schizophrenic raccoons
import sys
sys.path.append('/usr/lib/python2.7/dist-packages')

from hp3parclient import client
from hp3parclient import exceptions as hpexceptions

parser = ConfigParser.SafeConfigParser()
parser.read('/etc/cinder/cinder.conf')
hp3pars = []
for section in parser.sections():
    if parser.has_option(section, 'volume_driver') \
            and 'hp_3par' in parser.get(section, 'volume_driver'):
        hp3pars.append(section)


# Listing methods for adding a dimension to the Monasca metric
def bad_url_list():
    bad_urls = []
    for section_name in hp3pars:
        client = get_client(section_name)
        if not client:
            bad_urls.append(section_name)
    return bad_urls
    # return "__".join(bad_urls)


def bad_cred_list():
    bad_creds = []
    for section_name in hp3pars:
        client = get_client(section_name)
        if client and not \
                cred_is_valid(section_name, client):
            bad_creds.append(section_name)
        elif client:
            client.logout()
    return bad_creds
    # return "__".join(bad_creds)


def bad_cpg_list():
    bad_cpgs = []
    for section_name in hp3pars:
        client = get_client(section_name)
        if client:
            creds = cred_is_valid(section_name, client)
            if creds and not cpg_is_valid(section_name, client):
                bad_cpgs.append(section_name)
            elif creds:
                client.logout()
    return bad_cpgs
    # return "__".join(bad_cpgs)


def bad_iscsi_list():
    bad_ips = []
    for section_name in hp3pars:
        if 'iscsi' in parser.get(section_name, 'volume_driver'):
            client = get_client(section_name)
            if client:
                creds = cred_is_valid(section_name, client)
                if creds and not iscsi_is_valid(section_name, client):
                    bad_ips.append(section_name)
                elif creds:
                    client.logout()
    return bad_ips
    # return "__".join(bad_ips)


# Config testing methods check if option values are valid
def get_client(section_name):
    """
    This tries to create a client and verifies the api url
    :return: The client if url is valid, None if invalid/missing
    """
    try:
        cl = client.HP3ParClient(parser.get(section_name, 'hp3par_api_url'))
        return cl
    except (hpexceptions.UnsupportedVersion, ConfigParser.NoOptionError):
        return None


def cred_is_valid(section_name, client):
    """
    This tries to login to the client to verify credentials
    :return: True if credentials are valid, False if invalid/missing
    """
    try:
        client.login(parser.get(section_name, 'hp3par_username'),
                     parser.get(section_name, 'hp3par_password'))
        return True
    except (hpexceptions.HTTPForbidden,
            hpexceptions.HTTPUnauthorized,
            ConfigParser.NoOptionError):
        return False


def cpg_is_valid(section_name, client):
    """
    This tests to see if a cpg exists on the 3PAR array to verify cpg name
    :return: True if cpg name is valid, False if invalid/missing
    """
    cpg_list = parser.get(section_name, 'hp3par_cpg').split(',')
    for cpg in cpg_list:
        try:
            client.getCPG(cpg.strip())
        except (hpexceptions.HTTPNotFound, ConfigParser.NoOptionError):
            return False
    return True


def iscsi_is_valid(section_name, client):
    """
    This gets the iSCSI target ports from the client and checks the provided
    iSCSI IPs.
    :return: False if any of the provided IPs are wrong
    """
    valid_ips = []
    try:
        ip_list = parser.get(section_name, 'hp3par_iscsi_ips').split(",")
    except ConfigParser.NoOptionError:
        return False
    for port in client.getPorts()['members']:
        if (port['mode'] == client.PORT_MODE_TARGET and
                port['linkState'] == client.PORT_STATE_READY and
                port['protocol'] == client.PORT_PROTO_ISCSI):
            valid_ips.append(port['IPAddr'])
    for ip_addr in ip_list:
        ip = ip_addr.strip().split(':')
        if ip[0] not in valid_ips:
            return False
    return True

from oslo_config import cfg
from hp3parclient import client
from hp3parclient import exceptions as hpexceptions

hp3par_opts = [
    cfg.StrOpt('volume_driver',
               default=''),
    cfg.StrOpt('hp3par_api_url',
               default='',
               help="3PAR WSAPI Server Url like "
                    "https://<3par ip>:8080/api/v1"),
    cfg.StrOpt('hp3par_username',
               default='',
               help="3PAR username with the 'edit' role"),
    cfg.StrOpt('hp3par_password',
               default='',
               help="3PAR password for the user specified in hp3par_username",
               secret=True),
    cfg.ListOpt('hp3par_cpg',
                default='',
                help="List of the CPG(s) to use for volume creation"),
    cfg.ListOpt('hp3par_iscsi_ips',
                default=[],
                help="List of target iSCSI addresses to use."),
]

CONF = cfg.CONF
CONF(default_config_files=['/etc/cinder/cinder.conf'])

sections = list(CONF.list_all_sections())

hp3pars = []

# register group for each section
for i in sections:
    CONF.register_group(cfg.OptGroup(name=i))
    CONF.register_opts(hp3par_opts, i)

# get just sections using hp_3par drivers
for section in sections:
    if 'hp_3par' in CONF[section].volume_driver:
        hp3pars.append(section)


# Listing methods for adding a dimension to the Monasca metric
def bad_url_list():
    bad_urls = []
    for section_name in hp3pars:
        if not get_client(section_name):
            bad_urls.append(section_name)
    return bad_urls


def bad_cred_list():
    bad_creds = []
    for section_name in hp3pars:
        cl = get_client(section_name)
        if cl and not \
                cred_is_valid(section_name, cl):
            bad_creds.append(section_name)
    return bad_creds


def bad_cpg_list():
    bad_cpgs = []
    for section_name in hp3pars:
        client = get_client(section_name)
        if client \
                and cred_is_valid(section_name, client) \
                and not cpg_is_valid(section_name, client):
            bad_cpgs.append(section_name)
    return bad_cpgs


def bad_iscsi_list():
    bad_ips = []
    for section_name in hp3pars:
        client = get_client(section_name)
        if client and cred_is_valid(section_name, client) and not \
                iscsi_is_valid(section_name, client):
            bad_ips.append(section_name)
    return bad_ips


# Config testing methods check if option values are valid
def get_client(section_name):
    try:
        cl = client.HP3ParClient(CONF[section_name].hp3par_api_url)
        return cl
    except hpexceptions.UnsupportedVersion:
        return None


def cred_is_valid(section_name, client):
    try:
        client.login(CONF[section_name].hp3par_username,
                     CONF[section_name].hp3par_password)
        return True
    except hpexceptions.HTTPForbidden, hpexceptions.HTTPUnauthorized:
        return None


def cpg_is_valid(section_name, client):
    for cpg in CONF[section_name].hp3par_cpg:
        try:
            client.getCPG(cpg.strip())
        except hpexceptions.HTTPNotFound:
            return False
    return True


def iscsi_is_valid(section_name, client):
    valid_ips = []
    for port in client.getPorts()['members']:
        if (port['mode'] == client.PORT_MODE_TARGET and
                port ['linkState'] == client.PORT_STATE_READY and
                port['protocol'] == client.PORT_PROTO_ISCSI):
            valid_ips.append(port['IPAddr'])
    for ip_addr in CONF[section_name].hp3par_iscsi_ips:
        ip = ip_addr.split(':')
        if ip[0] not in valid_ips:
            return False
    return True

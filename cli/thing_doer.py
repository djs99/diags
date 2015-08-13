"""
Reads cli.conf & does the things
"""

from oslo_config import cfg
import wsapi_conf
import sshClient

PREFIX = 'cinder_diagnostics/'
CONF = cfg.CONF
CONF(default_config_files=['cinder_diagnostics/cli.conf'])


def main():
    # register CLI section
    cli_grp = cfg.OptGroup(name='CLI', title='CLI settings')
    cli_opts = [
        cfg.BoolOpt('testing', default=False,
                    help=('True enables testing of CLI tool itself')),
        cfg.StrOpt('test_file', default='test.conf',
                   help=('Location of the test.conf file'))
    ]

    CONF.register_group(cli_grp)
    CONF.register_opts(cli_opts, cli_grp)

    # get and register SSH sections
    ssh_opts = [
        cfg.StrOpt('service', default='', help='cinder or nova'),
        cfg.StrOpt('host_ip', default=''),
        cfg.StrOpt('ssh_user', default=''),
        cfg.StrOpt('ssh_password', default=''),
        cfg.StrOpt('conf_source', default='',
                   help='Location of cinder.conf on the cinder node'),
        # cfg.StrOpt('conf_dest', default='',
        #            help='Destination for cinder.conf file')
    ]

    sections = list(CONF.list_all_sections())

    cinder_nodes = []
    nova_nodes = []

    for section_name in sections:
        if section_name != 'CLI':
            CONF.register_group(cfg.OptGroup(name=section_name))
            CONF.register_opts(ssh_opts, section_name)
            if CONF[section_name].service.lower() == 'cinder':
                cinder_nodes.append(section_name)
            elif CONF[section_name].service.lower() == 'nova':
                nova_nodes.append(section_name)

    copy_files(cinder_nodes)
    print 'Nova Errors: '
    nova_checks(nova_nodes)
    print 'Web Services Checks: '
    ws_checks(cinder_nodes)


def copy_files(cinder_nodes):
    for node in cinder_nodes:
            client = sshClient.Client(CONF[node].host_ip, CONF[node].ssh_user,
                                       CONF[node].ssh_password)
            client.get_file(CONF[node].conf_source, PREFIX+node)
            client.disconnect()


def nova_checks(nova_nodes):
    for node in nova_nodes:
        print '[%s]' % node
        client = sshClient.Client(CONF[node].host_ip, CONF[node].ssh_user,
                                   CONF[node].ssh_password)
        for pkg in ['sysfsutils', 'sg3-utils']:
            if client.execute("dpkg-query -W -f='${Status}\n' "+pkg) != \
                    'install ok installed':
                print '%s is missing the package %s' % (node, pkg)
        client.disconnect()


def ws_checks(cinder_nodes, section='all'):
    if CONF['CLI'].testing:
        print wsapi_conf.WSChecker(True, CONF['CLI'].conf_file).check_all()
    else:
        for node in cinder_nodes:
            print '[%s]' % node
            checker =wsapi_conf.WSChecker(PREFIX+node)
            if section == 'all':
                print checker.check_all()
            else:
                print checker.check_section(section)


if __name__ == '__main__':
    main()

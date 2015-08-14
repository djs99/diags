"""
Reads cli.conf & does the things
Currently just prints results
"""

from oslo_config import cfg
import wsapi_conf
import sshClient
import pkg_checks

PREFIX = 'cinder_diagnostics/'
CONF = cfg.CONF

ssh_opts = [
            cfg.StrOpt('service', default='', help='cinder or nova'),
            cfg.StrOpt('host_ip', default=''),
            cfg.StrOpt('ssh_user', default=''),
            cfg.StrOpt('ssh_password', default=''),
            cfg.IntOpt('ssh_port', default=22),
            cfg.StrOpt('conf_source', default='',
                       help='Location of cinder.conf on the cinder node')
]


class Reader(object):

    def __init__(self, is_test=False):
        self.cinder_nodes = []
        self.nova_nodes = []

        CONF(default_config_files=['cinder_diagnostics/cli.conf'])

        if is_test:
            self.test_parse()
        else:
            self.real_parse()

    def test_parse(self):
        for section_name in list(CONF.list_all_sections()):
            if section_name != 'CLI':
                CONF.register_group(cfg.OptGroup(name=section_name))
                CONF.register_opts(ssh_opts, section_name)
                CONF.register_opts([cfg.StrOpt('conf_dest',
                                   default=PREFIX+'test.conf')], section_name)
                if CONF[section_name].service.lower() == 'test':
                    self.cinder_nodes.append(section_name)
                    self.nova_nodes.append(section_name)

    def real_parse(self):
        for section_name in list(CONF.list_all_sections()):
            if section_name != 'CLI':
                CONF.register_group(cfg.OptGroup(name=section_name))
                CONF.register_opts(ssh_opts, section_name)
                CONF.register_opts([cfg.StrOpt('conf_dest',
                                   default='%s%s.conf' % (PREFIX,section_name))
                                    ], section_name)
                if CONF[section_name].service.lower() == 'cinder':
                    self.cinder_nodes.append(section_name)
                elif CONF[section_name].service.lower() == 'nova':
                    self.nova_nodes.append(section_name)

    def copy_files(self):
        for node in self.cinder_nodes:
            client = sshClient.Client(CONF[node].host_ip, CONF[node].ssh_user,
                                      CONF[node].ssh_password)
            client.get_file(CONF[node].conf_source, CONF[node].conf_dest)
            client.disconnect()


# do checkers  <-- just temporary to see behavior
def nova_checks(nova_nodes):
    for node in nova_nodes:
        print '[%s]' % node
        print pkg_checks.nova_check(CONF[node].host_ip, CONF[node].ssh_user,
                                    CONF[node].ssh_password)


def ws_checks(cinder_nodes, is_test=False, section='all'):
    for node in cinder_nodes:
        print '[%s]' % node
        checker = wsapi_conf.WSChecker(is_test, CONF[node].conf_dest)
        if section == 'all':
            print checker.check_all()
        else:
            print checker.check_section(section)


if __name__ == '__main__':
    reader = Reader()
    reader.copy_files()
    print '\nNova Package checks: '
    nova_checks(reader.nova_nodes)
    print '\nWeb Services Checks: '
    ws_checks(reader.cinder_nodes)

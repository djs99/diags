DIRECTORY = 'config/'
EXTENSION = '.tmp'
CLI_CONFIG = 'cli.conf'
NOVA_PACKAGES = [
    ('sysfsutils',  '2.1'),
    ('sg3-utils', '1.3'),
]
CINDER_PACKAGES = [('hp3parclient', '3.1.1')]

HP_DRIVERS = [
    ('hp_3par_fc', '2.0.0'),
    ('hp_3par_iscsi', '2.0.0'),
    ('hp_lefthand_iscsi', '1.0.0'),
    ('hpmsa_fc', '1.0'),
    ('hpmsa_iscsi', '1.0'),
    ('hp_xp_fc', None),
]

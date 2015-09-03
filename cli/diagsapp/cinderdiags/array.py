import argparse
import conf_reader
import logging

from cliff.lister import Lister


class CheckArray(Lister):
    """Check 3PAR array configuration options in the cinder.conf

    "Node"                  = Section name in cli.conf.  These must be unique.
    "cinder.conf Section"   = Section name in cinder.conf on a node. These must
                              be unique.
    "WS API"                = hp3par_api_url option for a section in
                              cinder.conf
    "Credentials"           = hp3par_username and hp3par_password options for a
                              section in cinder.conf
    "CPG"                   = hp3par_cpg option for a section in cinder.conf
    "iSCSI IP(s)"           = hp3par_iscsi_ips option for a section in
                              cinder.conf
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CheckArray, self).get_parser(prog_name)
        parser.formatter_class = argparse.RawTextHelpFormatter
        parser.add_argument('-test',
                            dest='test',
                            action='store_true',
                            help=argparse.SUPPRESS)
        parser.add_argument('-name',
                            nargs='?',
                            default='arrays',
                            help='defaults to checking array configurations')
        return parser

    def take_action(self, parsed_args):
        reader = conf_reader.Reader(parsed_args.test)
        reader.copy_files()
        result = reader.ws_checks(parsed_args.name)
        reader.cleanup()
        if len(result) < 1:
            raise ValueError("%s not found" % parsed_args.name)
        columns = (
            'Node',
            'cinder.conf Section',
            'WS API',
            'Credentials',
            'CPG',
            'iSCSI IP(s)',
            'Driver Installed',
        )

        data = []
        for arr in result:
            data.append((
                arr['node'],
                arr['name'],
                arr['url'],
                arr['cpg'],
                arr['credentials'],
                arr['iscsi'],
                arr['driver'],
            ))
        return (columns, data)

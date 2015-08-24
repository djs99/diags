import logging
from cliff.lister import Lister
import conf_reader


class CheckArray(Lister):
    "Show details about a specific array"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CheckArray, self).get_parser(prog_name)
        parser.add_argument('-test', dest='test', action='store_true',
                            help='check array will only look at cli.conf '
                                 'sections with "service=test"')
        parser.add_argument('arrayname', nargs='?', default='arrays',
                            help='defaults to checking all arrays')
        return parser

    def take_action(self, parsed_args):
        reader = conf_reader.Reader(parsed_args.test)
        reader.copy_files()
        result = reader.ws_checks(parsed_args.arrayname)
        if len(result) < 1:
            raise ValueError("%s not found" % parsed_args.arrayname)
        columns = ('Node', 'Name', 'WS API', 'Credentials', 'CPG',
                   'iSCSI IP(s)')

        data = []
        for arr in result:
            data.append( (arr['node'],
                          arr['name'],
                          arr['url'],
                          arr['credentials'],
                          arr['cpg'],
                          arr['iscsi']
                          ) )
        return (columns, data)

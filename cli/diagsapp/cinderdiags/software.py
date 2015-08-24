import logging
import conf_reader

from cliff.lister import Lister


class CheckSoftware(Lister):
    "Check whether or not required software is present."

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CheckSoftware, self).get_parser(prog_name)
        parser.add_argument('-test', dest='test', action='store_true',
                            help='check software will only look at cli.conf '
                                 'sections with "service=test"')
        parser.add_argument('software', nargs='?', default='all',
                            help='package to be checked')
        parser.add_argument('version', nargs='?', default='all',
                            help='minimum version required')
        return parser

    def take_action(self, parsed_args):
        reader = conf_reader.Reader(parsed_args.test)
        result = reader.nova_checks((parsed_args.software,
                                     parsed_args.version))

        columns = ('Nova Node', 'Software', 'Installed', 'Version')
        data = []
        for pkg in result:
            data.append( (pkg['node'],
                          pkg['name'],
                          pkg['installed'],
                          pkg['version']) )

        return (columns, data)
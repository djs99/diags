import logging
import conf_reader

from cliff.lister import Lister


class CheckSoftware(Lister):
    "Check whether or not required software is present."

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CheckSoftware, self).get_parser(prog_name)
        parser.add_argument('-package', dest='name', required=False,
                            nargs=1, metavar='PACKAGE-NAME',
                            help='Requires -service SERVICE-TYPE (cinder or ' \
                                 'nova) optional --min-version ' \
                                 'MINIMUM-VERSION')


        args, checktype = parser.parse_known_args()
        if args.name:
            parser.add_argument('-service', dest='serv', required=True,
                                choices=['cinder', 'nova'], nargs=1)
            parser.add_argument('--min-version', dest='version', nargs='?')


        parser.add_argument('-test', dest='test', action='store_true',
                    help='check software will only look at cli.conf '
                         'sections with "service=test"')

        return parser

    def take_action(self, parsed_args):
        reader = conf_reader.Reader(parsed_args.test)
        if parsed_args.name:
            result = reader.pkg_checks(parsed_args.name,
                                       parsed_args.serv, parsed_args.version)
        else:
            result = reader.pkg_checks('default')

        columns = ('Node', 'Software', 'Installed', 'Version')
        data = []
        for pkg in result:
            data.append( (pkg['node'],
                          pkg['name'],
                          pkg['installed'],
                          pkg['version']) )

        return (columns, data)

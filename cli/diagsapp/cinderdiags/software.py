import argparse
import conf_reader
import logging

from cliff.lister import Lister


class CheckSoftware(Lister):
    """
    check for required software and versions on Cinder and Nova nodes.

    output data:
        Node        Node names set by user in cli.conf, names must be unique
                        [example]
        Software    Software package name.
        Installed   Installation status of the package.
        Version     Software package version meets the minimum requirement.
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CheckSoftware, self).get_parser(prog_name)
        parser.formatter_class = argparse.RawTextHelpFormatter
        parser.add_argument('-name',
                            dest='name',
                            nargs='?',
                            metavar='PACKAGE-NAME',
                            help='Requires --service SERVICE-TYPE (cinder or '
                                 'nova) \nOptional --package-min-version '
                                 'MINIMUM-VERSION')

        args, checktype = parser.parse_known_args()
        if args.name:
            parser.add_argument('--service',
                                dest='serv',
                                required=True,
                                choices=['cinder', 'nova'])
            parser.add_argument('--package-min-version',
                                dest='version',
                                nargs='?')

        parser.add_argument('-test',
                            dest='test',
                            action='store_true',
                            help=argparse.SUPPRESS)
        return parser

    def take_action(self, parsed_args):
        reader = conf_reader.Reader(parsed_args.test)
        if parsed_args.name:
            result = reader.pkg_checks(parsed_args.name,
                                       parsed_args.serv,
                                       parsed_args.version)
        else:
            result = reader.pkg_checks()

        reader.cleanup()
        columns = ('Node', 'Software', 'Installed', 'Version')
        data = []
        for pkg in result:
            data.append((
                pkg['node'],
                pkg['name'],
                pkg['installed'],
                pkg['version']),
            )

        return (columns, data)

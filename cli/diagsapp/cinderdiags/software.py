from __future__ import absolute_import
import argparse
import logging

from . import conf_reader
from cliff.lister import Lister


class CheckSoftware(Lister):
    """check for required software and versions on Cinder and Nova nodes

    output data:
        Node                node names set by user in cli.conf, names must be
                            unique
                                [NODE-NAME]
        Software            software package name
                                defaults: hp3parclient, sysfsutils, sg3-utils
        Installed           installation status of the software package
        Version             software package version meets the minimum
                            requirement
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
            result = reader.software_check(parsed_args.name,
                                       parsed_args.serv,
                                       parsed_args.version)
        else:
            result = reader.software_check()

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

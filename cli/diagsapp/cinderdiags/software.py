#  (c) Copyright 2015 Hewlett Packard Enterprise Development LP
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import argparse
import logging

from cinderdiags import conf_reader
from cliff.lister import Lister


class CheckSoftware(Lister):
    """check for required software (and versions) on Cinder and Nova nodes

    output data:
        Node                node names set by user in cli.conf, names must be
                            unique
                                example: [NODE-NAME]
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
        parser.add_argument('-software',
                            dest='name',
                            nargs='?',
                            metavar='PACKAGE-NAME',
                            default='default',
                            help='may also provide "--package-min-version '
                                 'MINIMUM-VERSION"')
        parser.add_argument('-service',
                            dest='serv',
                            default='default',
                            choices=['cinder', 'nova'],
                            help='defaults to checking all nodes')

        parser.add_argument('-test',
                            dest='test',
                            action='store_true',
                            help=argparse.SUPPRESS)

        parser.add_argument('-conf-file',
                            dest='conf',
                            help='location of cli.conf (defaults to '
                                 '/etc/cinderdiags/cli.conf)')

        args, unknown = parser.parse_known_args()
        if args.name:
            parser.add_argument('--package-min-version',
                                dest='version',
                                nargs='?')
        return parser

    def take_action(self, parsed_args):
        reader = conf_reader.Reader(parsed_args.test, parsed_args.conf)
        result = reader.software_check(parsed_args.name,
                                       parsed_args.serv,
                                       parsed_args.version)

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

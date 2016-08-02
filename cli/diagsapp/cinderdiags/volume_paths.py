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


class CheckPaths(Lister):
    """get volume paths for Nova node

    output data:
        Paths               list of discovered volume paths, with attached volume name (if found)
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CheckPaths, self).get_parser(prog_name)
        parser.formatter_class = argparse.RawTextHelpFormatter

        parser.add_argument('-test',
                            dest='test',
                            action='store_true',
                            help=argparse.SUPPRESS)

        parser.add_argument('-conf-data',
                            dest='data',
                            help='json structure containing cli.conf data')

        parser.add_argument('-os-vars',
                            dest='vars',
                            help='json structure containing OpenStack '
                                 'environment variables required to run '
                                 'Cinder commands')

        parser.add_argument('-attached-volumes',
                            dest='volumes',
                            help='json structure containing volume names that '
                                 'are attached to Nova instances')

        return parser

    def take_action(self, parsed_args):
        reader = conf_reader.Reader(parsed_args.test,
                                    json_data=parsed_args.data)
        result = reader.volume_paths_check(parsed_args.vars,
                                           parsed_args.volumes)

        columns = ('Path', 'Attached Volume')
        data = []
        for path in result:
            data.append((
                path['path'],
                path['vol_name']),
            )

        return (columns, data)

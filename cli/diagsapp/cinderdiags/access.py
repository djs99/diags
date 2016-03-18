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


class CheckCredentials(Lister):
    """check for valid SSH credentials to nova/cinder nodes

    output data:
        Node                node names set by user in cli.conf, names must be
                            unique
                                example: [NODE-NAME]
        Connect             ssh credentials can sucessfully connect to node
    """

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CheckCredentials, self).get_parser(prog_name)
        parser.formatter_class = argparse.RawTextHelpFormatter
        parser.add_argument('-conf-file',
                            dest='conf',
                            help='location of cli.conf (defaults to '
                                 '/etc/cinderdiags/cli.conf)')

        parser.add_argument('-conf-data',
                            dest='data',
                            help='json structure contain cli.conf data')

        return parser

    def take_action(self, parsed_args):
        reader = conf_reader.Reader(False,
                                    parsed_args.conf,
                                    parsed_args.data)
        result = reader.credentials_check()

        columns = ('Node', 'Connect')
        data = []
        for pkg in result:
            data.append((
                pkg['node'],
                pkg['connect']),
            )

        return (columns, data)

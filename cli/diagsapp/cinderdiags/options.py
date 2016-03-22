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

log = logging.getLogger(__name__)


class CheckOptions(Lister):
    """check 3PAR options in cinder.conf against 3PAR array(s)

    output data:
        Node                node names set by user in cli.conf, must be unique
                                example: [NODE-NAME]
        Backend Section     backend section names set by user in cinder.conf,
                            must be unique per node
                                example: [BACKEND-SECTION-NAME]
        WS API              web service API url for array
                                option: hpe3par_api_url
        Credentials         username and password for array
                                option: hpe3par_username, hpe3par_password
        CPG(s)              CPGs to use for volume creation
                                option: hpe3par_cpg
        iSCSI IP(s)         array's iSCSI IP addresses to use
                                option: hpe3par_iscsi_ips (multiple) or
                                        iscsi_ip_address (single)
        Driver              array's volume driver
                                option: volume_driver
    """

    def get_parser(self, prog_name):
        parser = super(CheckOptions, self).get_parser(prog_name)
        parser.formatter_class = argparse.RawTextHelpFormatter
        parser.add_argument('-test',
                            dest='test',
                            action='store_true',
                            help=argparse.SUPPRESS)
        parser.add_argument('-backend-section',
                            dest='name',
                            nargs='?',
                            default='arrays',
                            help='defaults to checking all backend sections')
        parser.add_argument('-conf-file',
                            dest='conf',
                            help='location of cli.conf (defaults to '
                                 '/etc/cinderdiags/cli.conf)')
        parser.add_argument('-conf-data',
                            dest='data',
                            help='json structure contain cli.conf data')
        parser.add_argument('-incl-system-info',
                            dest='info',
                            action='store_true',
                            help=argparse.SUPPRESS)
        return parser

    def take_action(self, parsed_args):
        reader = conf_reader.Reader(parsed_args.test,
                                    parsed_args.conf,
                                    parsed_args.data,
                                    parsed_args.info)
        result = reader.options_check(parsed_args.name)
        if len(result) < 1:
            raise ValueError("%s not found" % parsed_args.name)

        columns = ()
        columns_base = (
                'Node',
                'Backend Section',
                'WS API',
                'Credentials',
                'CPG',
                'iSCSI IP(s)',
                'Driver',
            )
        if parsed_args.info:
            columns = columns_base + ('System Info', 'Conf Items')
        else:
            columns = columns_base


        data = []

        for arr in result:
            entry = ()
            entry_base = (
                arr['node'],
                arr['name'],
                arr['url'],
                arr['credentials'],
                arr['cpg'],
                arr['iscsi'],
                arr['driver'],
            )
            if parsed_args.info:
                entry = entry_base + (arr['system_info'], arr['conf_items'])
            else:
                entry = entry_base

            data.append(entry)

        return (columns, data)

import logging
import os

from cliff.lister import Lister


class CheckArray(Lister):
    "Show details about a specific array"

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CheckArray, self).get_parser(prog_name)
        parser.add_argument('arrayname', nargs='+', default='')
        return parser

    def take_action(self, parsed_args):
        columns = ('Test', 'Status')

        # Replace with data from library call...
        data = []
        data.append( ("WS API", "OK") )
        data.append( ("credentials", "OK") )
        data.append( ("CPG", "OK") )
        data.append( ("iSCSI IP", "FAILED") )

        return (columns, data)

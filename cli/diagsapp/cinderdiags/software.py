import logging
import conf_reader

from cliff.lister import Lister


class CheckSoftware(Lister):
    "Check whether or not required software is present."

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(CheckSoftware, self).get_parser(prog_name)
        parser.add_argument('software', nargs='?', default='all')
        parser.add_argument('version', nargs='?', default='all')
        return parser

    def take_action(self, parsed_args):
        reader = conf_reader.Reader()
        result = reader.nova_checks((parsed_args.software,
                                     parsed_args.version))
        print result

        columns = ('Software', 'Installed', 'Version')
        data = []
        for pkg in result:
            data.append( (pkg['name'], pkg['installed'], pkg['version']) )

        # Replace with data from library call...
        # data = []
        # data.append( ("3PAR driver", "Installed") )
        # data.append( ("hp3parclient", "Missing") )
        # data.append( ("sysfsutils", "Installed") )
        # data.append( ("SG3-utils", "Bad Version") )

        return (columns, data)

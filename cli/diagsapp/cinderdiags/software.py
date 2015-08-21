import logging
import os

from cliff.lister import Lister


class CheckSoftware(Lister):
    "Check whether or not required software is present."

    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        columns = ('Software', 'Status')

        # Replace with data from library call...
        data = []
        data.append( ("3PAR driver", "Installed") )
        data.append( ("hp3parclient", "Missing") )
        data.append( ("sysfsutils", "Installed") )
        data.append( ("SG3-utils", "Bad Version") )

        return (columns, data)

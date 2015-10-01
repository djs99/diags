import json
import time
import re
import logging
from monasca_agent.collector.checks import AgentCheck
from cinder_diagnostics import config_tester

log = logging.getLogger(__name__)


class Diagnostics(AgentCheck):

    def check(self, instance):
        """
        This check reads JSON text outputted by logstash. It uses
        For reliability it reads 2 files at a staggered interval
        """

        error_dict = {}

        error_dict.update(self.read_file(instance.get('logpath1')))
        time.sleep(1)  # wait so files are staggered
        error_dict.update(self.read_file(instance.get('logpath2')))

        for uuid in error_dict:
            # strip all dimensions of forbidden characters
            for dim in error_dict[uuid]:
                error_dict[uuid][dim] = \
                    re.sub(r'[><=()\'\\;&\{\}\",\^]', '',
                           error_dict[uuid][dim].replace(' ', '_'))
            dimensions = self._set_dimensions(error_dict[uuid], instance)
            self.increment('CinderDiagnostics.' + error_dict[uuid][
                'error_type'], dimensions=dimensions)

    @staticmethod
    def read_file(path):
        """
        Reads and clears the logstash output file.
        """
        error_dict = {}
        try:
            f = open(path, 'r+')
            for line in iter(f):
                try:
                    data = json.loads(line)
                    dims = {'service': data['type'],
                            'hostname': data['host'],
                            'error': data['log_message'],
                            'cause': data['possible_cause'],
                            'error_type': data['name'],
                            'comments': data['comments'],
                            }
                    error_dict[data['@uuid']] = dims
                except (ValueError, KeyError):
                    log.warn(
                        'Incorrectly formatted line: "%s" in file %s. Check '
                        'your Logstash configuration.' % (line, path))
            # return to the beginning of the file and clear it
            f.seek(0)
            f.truncate()
            f.close()
        except IOError:
            log.error(
                'Unable to open %s. Check that Logstash is running'
                ' and permissions allow for read & write.  '
                'You may need to restart Logstash.' % path)
        return error_dict

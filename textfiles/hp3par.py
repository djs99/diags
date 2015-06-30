import json
import time
import re
import logging
import monasca_agent.collector.checks as checks

log = logging.getLogger(__name__)

class HP3PAR(checks.AgentCheck):

    def check(self, instance):
        """ This check reads json text outputted by logstash
            For reliability it reads 2 files at a staggered interval
        """

        error_dict = {}

        error_dict.update(self.read_file(instance.get('logpath1')))
        time.sleep(1)  # wait so files are staggered
        error_dict.update(self.read_file(instance.get('logpath2')))

        for key in error_dict:
            dimensions = self._set_dimensions(error_dict[key], instance)
            self.increment('0630-13.' + error_dict[key]['error_type'],
                           dimensions=dimensions)

    @staticmethod
    def read_file(path):
        error_dict = {}
        try:
            f = open(path, 'r+')
            for line in iter(f):
                try:
                    data = json.loads(line.replace(" ", "_"))
                    #  these fields must be created by Logstash
                    dims = {'service': data['type'],
                            'hostname': data['host'],
                            'error': re.sub(
                                r'(\d{4}(-\d\d){2}_(\d\d:?){3}\.\d+_|\[+\w?\d+\w?|;\d+\w)',
                                "", data['message']),
                            'cause': data['possible_cause'],
                            'error_type': data['name']}
                    for dim in dims:  # forbidden characters for dimensions
                        dims[dim] = re.sub(r'[><=()\'\\;&\{\}\",\^\[\]]', "", dims[dim])
                    error_dict[data['@uuid']] = dims
                except (ValueError, KeyError):
                    log.warn('Incorrectly formatted line: "%s" in file %s.  '
                             ' Check your Logstash configuration.' % (line, path))
            f.seek(0)
            f.truncate()
            f.close()
        except IOError:
            log.error(
                'Unable to open %s. Check that Logstash is running'
                ' and permissions allow for read & write.  '
                'You may need to restart Logstash.' % path)
        return error_dict

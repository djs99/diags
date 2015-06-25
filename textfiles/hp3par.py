import json
import time
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
            self.increment('HP3PAR.' + error_dict[key]['error_type'], dimensions=dimensions)


    @staticmethod
    def read_file(path):
        error_dict = {}
        try:
            f = open(path, 'r+')
            for line in iter(f):
                try:
                    data = json.loads(line.replace(" ", "_"))
                    dims = {'service': data['type'],
                            'hostname': data['host'],
                            'error': data['message'],
                            'cause': data['possible_cause'],
                            'error_type': data['name']}
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

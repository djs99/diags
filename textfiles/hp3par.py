import json
import time
import logging
import monasca_agent.collector.checks as checks

log = logging.getLogger(__name__)

class HP3PAR(checks.AgentCheck):

    def check(self, instance):
        """ This check opens a text file created by logstash
            Creates a metric for each error in that file
            Empties the file to avoid duplication
         """
        f1 = '/home/vagrant/monasca-logs/3par1.txt'
        f2 = '/home/vagrant/monasca-logs/3par2.txt'

        error_dict = {}

        error_dict.update(self.read_file(f1))
        time.sleep(1)  # wait so files are staggered
        error_dict.update(self.read_file(f2))

        for key in error_dict:
            dimensions = self._set_dimensions(error_dict[key], instance)
            self.increment('HP3PAR.method.' +
                           error_dict[key]['error_type'],
                           dimensions=dimensions)

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
                    error_dict[line] = dims
                except (ValueError, KeyError):
                    log.warn('Incorrectly formatted line: %s' % line)
            f.seek(0)
            f.truncate()
            f.close()
        except IOError:
            raise Exception(
                'Unable to open %s. Check that the file exists and that '
                'permissions allow for read & write.' % path)
        return error_dict



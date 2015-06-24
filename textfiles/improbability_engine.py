import time
import binascii
import socket
import monasca_agent.collector.checks as checks
import json


class Improb(checks.AgentCheck):

    def check(self, instance):
        """Example stats """
       
        #self.log.warn(dimensions)   #Debug hack: should log "...{'hostname': 'devstack'}

        #setup the connection. Url and port are pulled from improbability_engine.yaml
        TCP_IP = instance.get('url', '')
        TCP_PORT = instance.get('port', '')
        BUFFER_SIZE = 4096
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((TCP_IP, TCP_PORT))
        s.listen(1)
        s.settimeout(3)      #3 seconds, because Logstash client tries to connect every 2 seconds
        try:
            conn, addr = s.accept()
        except:
            return
        

        #If agent is a client
#        s.settimeout(15)
#        data = True  #go though the while loop once
#        while data:
#            try:
#                data = s.recv(BUFFER_SIZE)
#                if not data:
#                    break
#                self.log.warn(data)
#            except:
#                self.log.warn("No log entries received")
#                break
#        s.shutdown(0)
#        s.close()

        #If agent is a server
        total_data = []
        while 1:
            try:
                data = conn.recv(BUFFER_SIZE)
                if not data: break
                total_data.append(data)
                self.log.warn(data)     #Debug: logs the message. Replace with code to add message to metrics/measurements/dimensions as needed
            except:
                #self.log.warn(data)
                break
        s.shutdown(0)
        s.close()
        if total_data:
            for message in total_data:
                line = json.loads(message.replace(" ", "_"))
                dimensions = self._set_dimensions({'service': line['type'],
                                           'hostname': line['host'],
                                           'error': line['message'],
                                           'cause': line['possible_cause']},
                                           instance)

                self.increment('0622.HP3PAR.rename.' + line['name'],
                                dimensions=dimensions)





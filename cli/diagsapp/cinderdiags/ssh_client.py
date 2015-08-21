import paramiko
import logging

logger = logging.getLogger(__name__)


class Client(object):

    def __init__(self, hostName, sshUserName, sshPassword):
        """ Connect and perform action to remote machine using SSH
        """
        try:
                # Connect to remote host
                self.client = paramiko.SSHClient()
                self.client.set_missing_host_key_policy(
                    paramiko.AutoAddPolicy())
                self.client.connect(hostName, username=sshUserName,
                                password=sshPassword)

        except IndexError:
            pass
        except paramiko.ssh_exception:


    def get_file(self, fromLocation, toLocation):
        """ perform copy action to remote machine using SSH
        """
        try:
                # Setup sftp connection and transmit this script
                sftp = self.client.open_sftp()
                sftp.get(fromLocation, toLocation)
                sftp.close()

        except IndexError:
            pass


    def disconnect(self):
        """ perform copy action to remote machine using SSH
        """
        try:
                self.client.close()

        except IndexError:
            pass

    def execute(self, command):
                # Run the transmitted script remotely without args and show its output.
                # SSHClient.exec_command() returns the tuple (stdin,stdout,stderr)
                stdout = self.client.exec_command(command)[1]
                return stdout.read()

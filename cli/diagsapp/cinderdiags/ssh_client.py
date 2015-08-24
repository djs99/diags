import paramiko
import logging
import socket

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
                                password=sshPassword, timeout=20)

        except socket.error:
            logger.error('Invalid host_ip %s' % hostName)

        except paramiko.ssh_exception.AuthenticationException:
                logger.error('Invalid ssh credentials for %s in cli.conf' %
                             hostName)

    def get_file(self, fromLocation, toLocation):
        """ perform copy action to remote machine using SSH
        """
        if self.client.get_transport() and \
                self.client.get_transport().is_authenticated():
            try:
                    # Setup sftp connection and transmit this script
                    sftp = self.client.open_sftp()
                    sftp.get(fromLocation, toLocation)
                    sftp.close()

            except (IOError, paramiko.ssh_exception.SSHException):
                logger.warning('Unable to copy %s. Verify path in cli.conf' %
                               fromLocation)

    def disconnect(self):
        """ perform copy action to remote machine using SSH
        """
        self.client.close()

    def execute(self, command):
        # Run the transmitted script remotely without args and show its output.
        # SSHClient.exec_command() returns the tuple (stdin,stdout,stderr)
        if self.client.get_transport() and \
                self.client.get_transport().is_authenticated():
            try:
                stdout = self.client.exec_command(command, timeout=20)[1]
                return stdout.read()
            except paramiko.ssh_exception.SSHException:
                logger.warning('Cannot check packages. '
                               'Check SSH credentials in cli.conf.')

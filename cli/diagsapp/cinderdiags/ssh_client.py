#  (c) Copyright 2015 Hewlett Packard Enterprise Development LP
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import paramiko
import socket


class Client(object):

    def __init__(self, hostName, sshUserName, sshPassword):
        """ Connect and perform action to remote machine using SSH
        """
        try:
            # Connect to remote host
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(hostName,
                                username=sshUserName,
                                password=sshPassword,
                                timeout=20)

        except socket.error:
            raise Exception("SSH Error: Unable to connect")
        except paramiko.ssh_exception.AuthenticationException:
            raise Exception("SSH Error: Invalid SSH credentials")

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
                return toLocation

            except (IOError, paramiko.ssh_exception.SSHException):
                raise Exception("SSH Error: Unable to copy %s" % fromLocation)

    def disconnect(self):
        """ perform copy action to remote machine using SSH
        """
        self.client.close()

    def execute(self, command):
        # Run the transmitted script remotely without args and show its output.
        # SSHClient.exec_command() returns the tuple (stdin, stdout, stderr)
        if self.client.get_transport() and \
                self.client.get_transport().is_authenticated():
            try:
                resp = self.client.exec_command(command, timeout=20)
                stdout = resp[1].readlines()
                stderr = resp[2].readlines()
                return ''.join(stdout) + ''.join(stderr)

            except (paramiko.ssh_exception.SSHException, socket.timeout):
                raise Exception("SSH Error: Unable to execute remote command "
                                "(%s)" % command)

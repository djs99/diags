import sys
import os.path
import paramiko
import time
import subprocess
       
def executeCommand(hostName, sshUserName, sshPassword , command, filesToCopy = []) :
    """ Connect and perform action to remote machine using SSH 
    """
    
    try:
            # Connect to remote host
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostName, username=sshUserName, password=sshPassword)
           
            # Setup sftp connection and transmit this script
            sftp = client.open_sftp()
            for f in filesToCopy :
               if os.path.isfile(f):
                  sftp.put(f, f)
            sftp.close()
            
            #Executing error injection on the remote machine
            #print error
            output = execute(client, command)
             
            # Removing file from the remote machine
            for f in filesToCopy :
               if os.path.isfile(f):
                 execute(client, 'rm -rf ' +f)
              
            client.close()
            return output
    except IndexError:
        pass

def execute(client, command ):
            response = []
            # Run the transmitted script remotely without args and show its output.
            # SSHClient.exec_command() returns the tuple (stdin,stdout,stderr)
            stdout = client.exec_command(command)[1]
            output = stdout.readlines()
            for line in output:
                # Process each line in the remote output
                  response.append(line)
            return response

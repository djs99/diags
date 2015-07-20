import sshClient
from Config import *

client = sshClient.connect(Config().devstackVM, Config().devstackSshUser, Config().devstackSshPassword)
sshClient.execute(client, "touch setup.sh")
sshClient.execute(client, "touch cinderDiagnostics.yaml")
sshClient.execute(client, "touch cinderDiagnostics.conf")
sshClient.execute(client, "touch cinderDiagnostics.py")
sshClient.copyFile(client, "setup.sh","setup.sh")
sshClient.copyFile(client, "../textfiles/cinderDiagnostics.conf", "cinderDiagnostics.conf")
sshClient.copyFile(client, "../textfiles/cinderDiagnostics.yaml", "cinderDiagnostics.yaml")
sshClient.copyFile(client, "../textfiles/cinderDiagnostics.py", "cinderDiagnostics.py")
sshClient.execute(client, "sudo chmod 777 setup.sh")
sshClient.execute(client, "./setup.sh")
sshClient.disconnect(client)
    
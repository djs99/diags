#!/usr/bin/env python
#---------------------------------------------------------------------------------------
# Helion Diagnostic V1 testing
#
#---------------------------------------------------------------------------------------
import sys
import os.path
import argparse
#import ConfigParser
from Config import *
from sshClient import *
import sys


app = "Helion Diagnostic V1"


# Configure command line arguments
#---------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(usage="./Inject.py [options]...\nExecute without arguments to pull from 'Properties.cfg'\n")

parser.add_argument("--debug", dest="debug", action="store_true", help="List out given params")

# Errors
parser.add_argument("--bad_3par_credential", dest="bad_3par_credential", action="store_true", help="inject 3par bad credential")
parser.add_argument("--bad_3par_cpg", dest="bad_3par_cpg", action="store_true", help="inject 3par bad cpg")

# Devstack arguments
#parser.add_argument("--devstack-vm", dest="devstackVM", help="Host address to use as devstack target")
#parser.add_argument("--devstack-ssh-user", dest="devstackSshUser", help="Username to use for SSH on Devstack target")
#parser.add_argument("--devstack-ssh-password", dest="devstackSshPassword", help="Password to use for SSH on Devstack target")
#parser.add_argument("--conder-configuration-file", dest="cinderConfLocation", help="Cinder Config file location to use for error injection")


args = parser.parse_args()

# Parse configuration from command line and config file
#---------------------------------------------------------------------------------------
# Pull in configuration from config file
#if os.path.isfile("Properties.cfg"):
#    config = ConfigParser.RawConfigParser()
#    config.read("Properties.cfg")
#    if config.has_option('Devstack', 'devstack_host'): Config().devstackVM = config.get('Devstack', 'devstack_host') 
#    if config.has_option('Devstack', 'devstack_ssh_username'): Config().devstackSshUser = config.get('Devstack', 'devstack_ssh_username') 
#    if config.has_option('Devstack', 'devstack_ssh_password'): Config().devstackSshPassword = config.get('Devstack', 'devstack_ssh_password') 
#    if config.has_option('Devstack', 'cinder_config_location'): Config().cinderConfigLocation = config.get('Devstack', 'cinder_config_location')
#    if config.has_option('Devstack', 'cinder_log_location'): config().cinderLogLocation = config.get('Devstack', 'cinder_log_location')

# Pull in configuration from command line
#if len(sys.argv) > 1:
    # Set custom Devstack target
#    if args.devstackVM: Config().devstackVM = args.devstackVM
#    if args.devstackSshUser: Config().devstackSshUser = args.devstackSshUser
#    if args.devstackSshPassword: Config().devstackSshPassword = args.devstackSshPassword
#    if args.cinderConfigLocation: Config().cinderConfigLocation = args.cinderConfigLocation
    

# List params that were read in
if args.debug:
   Config().PrintUserSetConfigs()
   sys.exit(0)

# Execute Test
#---------------------------------------------------------------------------------------
if len(sys.argv) > 1 :
  filesToCopy = ["ErrorInjection.py", "ErrorLog.py"]
  executeCommand(Config().devstackVM, Config().devstackSshUser, Config().devstackSshPassword, "python ErrorInjection.py " +sys.argv[1], filesToCopy)
else :
  print "Provide name of error"

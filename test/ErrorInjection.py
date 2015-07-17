#!/usr/bin/python

import os
import shutil
import time
import sys
import argparse
import os.path
import subprocess
import threading
import ConfigParser


class CinderErrors(object):
	'''
	Inject cinder configuration error
	'''
	cinder_config = "/etc/cinder/cinder.conf"
  

	def stop_cinder_service(self):
            output= os.popen("sudo service cinder-volume stop").read()
	    if 'cinder-volume stop/waiting' not in output:
	        print ('Something Went Wrong, Could not able to stop Cinder-Volume:', output)
	    

	def start_cinder_service(self):
           output= os.popen("sudo service cinder-volume start").read()
	   if 'cinder-volume start/running' not in output:
	       print ('Something Went Wrong, Could not able to start Cinder-Volume:', output)
	   
	
        def restart_cinder_service(self):
            output= os.popen("sudo service cinder-volume restart").read()
	    if 'cinder-volume start/running' not in output:
	        print ('Something Went Wrong, Could not able to Restart Cinder-Volume:', output)
	
        def is_cinder_service_running(self):

		return true;
  
  
        def bad_3par_credential(self, badUserName, badPassword):
            #print "Injecting bad 3par credential"
            badCredential={'hp3par_username' : badUserName, 'hp3par_password' : badPassword}
            self.inject_error_in_cinder_configuration(badCredential,"3PAR-SLEEPYKITTY-FC")
            

        def bad_3par_cpg(self, badCpg):
            #print "Injecting bad 3par cpg"
            badCpg={'hp3par_cpg' : badCpg}
            self.inject_error_in_cinder_configuration(badCpg,"3PAR-SLEEPYKITTY-FC")
            
            
        def missing_package_3parclient(self):
            self.inject_missing_package_error('hp3parclient')
            

       	#def inject_error_in_cinder_configuration(self , dict) :
       	#	self.stop_cinder_service()
    	#	backup_cinder_config= self.cinder_config +".origin"
	#	os.rename(self.cinder_config , backup_cinder_config)
        #       try :
	#		r = open(backup_cinder_config, 'r')
	#		w = open(self.cinder_config, 'w')		
	#	        for line in r:
        #                   for key in dict.keys():
	#		        if line is not None and line.startswith(key):
	#			    z = key+"="+dict.get(key)
	#		            w.write(key+"="+dict.get(key)+"\n")
	#		        else:
	#			    w.write(line)
        #        finally :
	#		 r.close()
	#		 w.close()
	#		 self.start_cinder_service();
	#		 time.sleep(12)
	#      	os.remove(self.cinder_config) 
        #	os.rename(backup_cinder_config , self.cinder_config)    
        #	self.restart_cinder_service();
        
        def inject_missing_package_error(self, package_name) :
            try :  
                cmnd = "yes | sudo -H pip  uninstall " + package_name
                os.popen(cmnd)
                time.sleep(5)
                self.restart_cinder_service();
                time.sleep(15)
            
            except: # catch *all* exceptions
                          print sys.exc_info()[0]    
            finally :
                # Install package again
                cmnd = "yes | sudo -H pip install " + package_name
                os.popen(cmnd)
                time.sleep(5)
                self.restart_cinder_service();
   
        def inject_error_in_cinder_configuration(self , dict, section) :

	   if os.path.isfile(self.cinder_config):
	
                backup_cinder_config= self.cinder_config +".origin"
		os.rename(self.cinder_config , backup_cinder_config)
                try :
                  
                   config = ConfigParser.RawConfigParser(allow_no_value=True)
                   config.read(backup_cinder_config)
                   if config.has_section(section):
                      for key in dict.keys():
                          config.set(section,key,dict.get(key))
                   else :
                      print "Cinder conf does not cotanin the 3PAR configuration "
                   # Writing our configuration file to 'cinder.conf'
                   with open(self.cinder_config, 'w') as configfile:
                        config.write(configfile)
                   self.restart_cinder_service();
                   time.sleep(15)
                except: # catch *all* exceptions
                          print sys.exc_info()[0]
                 
                finally :
                    
                    if os.path.isfile(self.cinder_config):
                       os.remove(self.cinder_config) 
  	               os.rename(backup_cinder_config , self.cinder_config)    
  	            if os.path.isfile(backup_cinder_config):
                       os.rename(backup_cinder_config , self.cinder_config) 
                    self.restart_cinder_service();
           else :
                 print "No file present : " + self.cinder_config


cinder_log_path = '/var/log/cinder/temp.log'
# To verify the string we just keeping log in temprary file and checking if error message is logged or not 
class LogCapture(threading.Thread):
        

        def __init__(self):
                threading.Thread.__init__(self)
        def run(self):
                log_write_cmd = 'tail -f /var/log/cinder/cinder-volume.log >> /var/log/cinder/temp.log'
                global proc
                proc = subprocess.Popen(log_write_cmd, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
        def terminate_thread(self):
                try:
                        proc.terminate()
                except:
                        raise
        def cleanup(self):
            if os.path.isfile(cinder_log_path):
                os.remove(cinder_log_path)



class LogVerify:
        

        def __init__(self, log):
                self.log = log

        def check_log_for_bad_3par_credential(self):
                cmd = "grep 'Forbidden (HTTP 403) 5 - invalid username or password' " +cinder_log_path
                proc = subprocess.Popen (cmd, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
                line = proc.stdout.readlines()
                isInjected = False
                for error in line:
                        if 'Forbidden (HTTP 403) 5 - invalid username or password' in error:
                                print "Error bad_3par_credential Injected Successfully "
                                print  line
                                isInjected = True
                                break
                if not isInjected :
                  print "Error bad_3par_credential Injected UnSuccessfully "
                    
        def check_log_for_bad_3par_cpg(self):

                cmd1 = '''grep "Invalid input received: CPG (badcpg) doesn't exist on array" ''' +cinder_log_path
                proc = subprocess.Popen (cmd1, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
                line = proc.stdout.readlines()
                isInjected = False
                for error in line:
                        if "Invalid input received: CPG (badcpg) doesn't exist on array" in error:
                                print "Error bad_3par_cpg Injected Successfully "
                                print  line
                                isInjected = True
                                break
                if not isInjected :
                  print "Error bad_3par_cpg Injected UnSuccessfully "              

        def check_log_for_missing_package_3parclient(self):
            cmnd = '''grep "You must install hp3parclient before using 3PAR drivers" ''' + cinder_log_path
            proc = subprocess.Popen(cmnd, stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
            lines = proc.stdout.readlines()
            isInjected = False
            for errLine in lines:
                if "You must install hp3parclient before using 3PAR drivers" in errLine:
                    print "Error missing_package_3parclient Injected Successfully "
                    print errLine
                    isInjected = True
                    break
            if not isInjected :
                print "Error missing_package_3parclient Injected UnSuccessfully "
                         




#....................................Command Line argument......................................................................
parser = argparse.ArgumentParser(usage="./ErrorInjection.py [options]...\nExecute'\n")
parser.add_argument("--debug", dest="debug", action="store_true", help="List out given params")
# Errors
parser.add_argument("--bad_3par_credential", dest="bad_3par_credential", action="store_true", help="inject 3par bad credential")
parser.add_argument("--bad_3par_cpg", dest="bad_3par_cpg", action="store_true", help="inject 3par bad cpg")
parser.add_argument("--missing_package_3parclient", dest="missing_package_3parclient", action="store_true",
                        help="inject missing package 3parclient")

#................................................ Start Injection..................................................................
log = LogCapture()
log.start()
log_verify = LogVerify(1)
cinder = CinderErrors()
args = parser.parse_args()

if len(sys.argv) > 1:
#  error = sys.argv[1]
  if args.bad_3par_credential :
     cinder.bad_3par_credential("bad3paradm","bad3pardata")
     log_verify.check_log_for_bad_3par_credential()

  elif args.bad_3par_cpg :
     cinder.bad_3par_cpg("badcpg")
     log_verify.check_log_for_bad_3par_cpg()
     
  elif args.missing_package_3parclient :
     cinder.missing_package_3parclient()
     log_verify.check_log_for_missing_package_3parclient()
  else : 
    print ' Error Injection does not support : ' + sys.argv[1]
cinder.restart_cinder_service()
log.terminate_thread()
log.cleanup()
#................................................ End Injection..................................................................
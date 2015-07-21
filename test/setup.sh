logfile1="/var/log/cinder-diagnostics/errorlog1.txt"
logfile2="/var/log/cinder-diagnostics/errorlog2.txt"
cinder_diagnostics_log="/var/log/cinder-diagnostics"
monasca_lib_agent="/etc  /monasca/agent/conf.d/"
monasca_agent="/usr/lib/monasca/agent/conf.d/"
cinder_diagnostics_conf="cinderDiagnostics.conf"
cinder_diagnostics_yaml="cinderDiagnostics.yaml"
cinder_diagnostics_py="cinderDiagnostics.py"
logstash="logstash-1.5.0/"
# Install 3PAR client
 sudo -H pip install hp3parclient
# Restart volume services
 sudo service cinder-volume restart
# install Java
 sudo apt-get --assume-yes  install default-jre

if [ ! -d "$logstash" ]; then
     curl -O https://download.elasticsearch.org/logstash/logstash/logstash-1.5.0.tar.gz
     tar -zxvf logstash-1.5.0.tar.gz
fi

if [ ! -d "$cinder_diagnostics_log" ]; then
   sudo mkdir $cinder_diagnostics_log
fi

if [ ! -d "$monasca_agent" ]; then
   sudo  mkdir $monasca_agent
fi

if [ ! -d "$monasca_lib_agent" ]; then
   sudo mkdir $monasca_lib_agent
fi

if [ ! -f "$logfile1" ]; then
   sudo touch $logfile1
fi

if [ ! -f "$logfile2" ]; then
   sudo touch $logfile2
fi


sudo cp  $cinder_diagnostics_yaml $monasca_agent/
sudo cp  $cinder_diagnostics_yaml $monasca_lib_agent/
sudo cp  $cinder_diagnostics_conf /home/vagrant/logstash-1.5.0/
sudo cp  $cinder_diagnostics_py  /usr/lib/monasca/agent/custom_checks.d/
sudo chmod 777 /var/log/cinder-diagnostics/*
sudo service monasca-agent restart



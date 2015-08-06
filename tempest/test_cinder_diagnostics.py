#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from tempest.api.monitoring import base
from tempest_lib import exceptions as lib_exc
from tempest import test
from tempest_lib.common.utils import data_utils
from tempest.common import waiters
import datetime
import json
from tempest.common import ssh
from tempest import config
import time
CONF = config.CONF

class MonitoringCinderDiagnosticsTestJSON(base.BaseMonitoringTest):
    _interface = 'json'

    @classmethod
    def setUpClass(cls):
        super(MonitoringCinderDiagnosticsTestJSON, cls).setUpClass()

    @test.attr(type="gate")
    def test_bad_3par_credentials(self):
        metric_name = "cinderDiagnostics.credentials"
        error_injection_name ="bad_3par_credential"
        self._test_cinder_diagnostics(metric_name, error_injection_name);
        
    @test.attr(type="gate")
    def test_bad_3par_cpg(self):
        metric_name = "cinderDiagnostics.CPG"
        error_injection_name ="bad_3par_cpg"
        self._test_cinder_diagnostics(metric_name, error_injection_name);
        
    @test.attr(type="gate")
    def test_missing_package_3parclient(self):
        metric_name = "cinderDiagnostics.3par"
        error_injection_name ="missing_package_3parclient"
        self._test_cinder_diagnostics(metric_name, error_injection_name);
        
    @test.attr(type="gate")
    def test_bad_3par_iscsi_ips(self):
        metric_name = "cinderDiagnostics.iSCSI"
        error_injection_name ="bad_3par_iscsi_ips"
        self._test_cinder_diagnostics(metric_name, error_injection_name);
    
    @test.attr(type="gate")
    def test_bad_3par_ws_url(self):
        metric_name = "cinderDiagnostics.WS"
        error_injection_name ="bad_3par_ws_url"
        self._test_cinder_diagnostics(metric_name, error_injection_name);
    
    #@test.attr(type="gate")
    def _test_missing_package_sg3utils(self):
        metric_name = "cinderDiagnostics.sg3utils"
        error_injection_name ="available_package_sg3utils"
        
        
        
        self.manager = self.os
        #self.adm_manager= self.os_adm
        self.image = CONF.compute.image_ref
        self.flavor = CONF.compute.flavor_ref
       
        #extra_specs = {"volume_backend_name":"3PAR-THEVERSE"}
        #self.adm_manager.volume_types_client.create_volume_type(name='3PAR-THEVERSE', extra_specs=extra_specs)
        
          # Step 1: create a volume 
        name = data_utils.rand_name("volume")
        volume = self.manager.volumes_client.create_volume(
            display_name=name, volume_type='3PAR-THEVERSE')
        self.manager.volumes_client.wait_for_volume_status(volume['id'],
                                                         'available')
        
        
        
        # Test normal case for successful connection on first try
        client = ssh.Client(CONF.cinder_diagnostics.cinder_ssh_ip, CONF.cinder_diagnostics.cinder_ssh_user, CONF.cinder_diagnostics.cinder_ssh_password, timeout=30)
        sshconnection = client._get_ssh_connection(sleep=1)
        try:
            # Setup sftp connection and transmit this script
            sftp = sshconnection.open_sftp()
            sftp.put("ErrorInjection.py", "ErrorInjection.py")
            sftp.close()
            client.exec_command("python ErrorInjection.py --missing_package_sg3utils")
            sshconnection.close()
        except IndexError:
            pass
        
       
        # Step 2: create vm instance
        vm_name = data_utils.rand_name("instance")
      
        server = self.manager.servers_client.create_server(
            vm_name, self.image, self.flavor)
        server_id = server['id']
        waiters.wait_for_server_status(self.manager.servers_client, server_id,
                                       'ACTIVE')
        # Step 3: attach and detach volume to vm
        
        self.manager.servers_client.attach_volume(server_id,
                                                  volume['id'],
                                                  '/dev/vdc')
        self.manager.volumes_client.wait_for_volume_status(volume['id'],
                                                           'in-use')
        self.manager.volumes_client.detach_volume(volume['id'])
        self.manager.volumes_client.wait_for_volume_status(volume['id'], 'available')
        
         # Step 5: delete volume
        self.manager.volumes_client.delete_volume(volume['id'])
        self.manager.volumes_client.wait_for_resource_deletion(volume['id'])
        
        # Step 4: delete vm
        self.manager.servers_client.delete_server(server_id)
        self.manager.servers_client.wait_for_server_termination(server_id)
       

       
        
        
        
        self._test_cinder_diagnostics(metric_name, error_injection_name);
    
    
 
    def _test_cinder_diagnostics(self,  metric_name, error_injection_name):
        
        
        m_starttime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        m_starttime = m_starttime.replace(' ', 'T') + 'Z'
        
        # Test case to check if new notification is created successfully.
        notification_name = data_utils.rand_name('notification-')
        notification_type = 'EMAIL'
        # Replace below email with valid email address as required.
        u_address = 'root@localhost'
        response = self.monitoring_client.create_notification(name=notification_name, type=notification_type, address=u_address)
        self.assertEqual(notification_name, response['name'])
        notification_id = response['id']
        # Delete notification
        # 
        
        #alarm_def_name = metric_name
        alarm_def_name = data_utils.rand_name('test_monasca_alarm_definition')
        expression = '%s > 0' % (metric_name)
        severity = 'HIGH'
        body = self.monitoring_client.create_alarm_definition(name=alarm_def_name, expression=expression, severity=severity)
        self.assertEqual(alarm_def_name, body['name'])
        alarm_def_id = body['id']
        self.assertEqual(expression, body['expression'])
        
        m_statistics = 'count'
        m_endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        m_endtime = m_endtime.replace(' ', 'T') + 'Z'
        body = self.monitoring_client.metric_statistics(name=metric_name, dimensions='service:cinder',
                     statistics=m_statistics, end_time=m_endtime, merge_metrics='true')
        self.assertEqual('200', body.response['status'])
        response = json.loads(body.data)
              
        
        # Test normal case for successful connection on first try
        client = ssh.Client(CONF.cinder_diagnostics.cinder_ssh_ip, CONF.cinder_diagnostics.cinder_ssh_user, CONF.cinder_diagnostics.cinder_ssh_password, timeout=100)
        sshconnection = client._get_ssh_connection(sleep=1)
        try:
            # Setup sftp connection and transmit this script
            sftp = sshconnection.open_sftp()
            sftp.put("ErrorInjection.py", "ErrorInjection.py")
            sftp.close()
        except IndexError:
            pass
        client.exec_command("python ErrorInjection.py --"+error_injection_name)
        
        isMetricAvailable = True
        for i in range(0, 30):
              metricFields = {'name': metric_name}
              #metricFields['timestamp'] = int((time.time()*1000))
              body = self.monitoring_client.list_metric(metricFields)
              self.assertEqual('200', body.response['status'])
              response = json.loads(body.data)
              if len(response['elements']) < 1 :
                   isMetricAvailable = False
                   
        
        isMeasurementsFound = False
        isAlarmFound = False
        isStateChangeToAlarm = False     
       
        
        for i in range(0, 30):
              m_statistics = 'count'
              m_endtime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
              m_endtime = m_endtime.replace(' ', 'T') + 'Z'
              body = self.monitoring_client.metric_statistics(name=metric_name, dimensions='service:cinder',
                     statistics=m_statistics,start_time=m_starttime, end_time=m_endtime, merge_metrics='true')
              self.assertEqual('200', body.response['status'])
              response = json.loads(body.data)
              if len(response['elements']) > 0 :
                  if len(response['elements'][0]['statistics']) ==  1:
                    isMeasurementsFound = True ;
                    break 
        
        for i in range(0, 60):
            body = self.monitoring_client.list_alarms(alarm_definition_id=alarm_def_id)
            if len(body['elements']) > 0:
               isAlarmFound = True
               if body['elements'][0]['state'] == 'ALARM' :
                  isStateChangeToAlarm = True
                  break 
            time.sleep(3) 
            
        self.monitoring_client.delete_notification(notification_id)
        self.monitoring_client.delete_alarm_definition(alarm_def_id)            
        
        if not isMetricAvailable :
             self.fail("No metric found " + metric_name )
        if not isMeasurementsFound and not isStateChangeToAlarm :
             self.fail("No measurements found for " + metric_name ) 
        if not isAlarmFound :
             self.fail("No alarm found for " + metric_name )
        if not isStateChangeToAlarm :
             self.fail("No state change to ALARM  for  metric " + metric_name )
     
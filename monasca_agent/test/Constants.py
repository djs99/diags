#uri's
volumes_uri="/rest/storage-volumes"
login_session_uri="/rest/login-sessions"
fc_networks_uri="/rest/fc-networks"
storage_pools_uri="/rest/storage-pools"
fc_sans_endpoints_uri="/rest/fc-sans/endpoints"
volume_attachments_uri="/rest/storage-volume-attachments"
storage_systems_uri="/rest/storage-systems"
connections_uri="/rest/connections"
attachable_volumes_uri="/rest/storage-volumes/attachable-volumes"
#operation constants
create_volume="create_volume"
delete_volume="delete_volume"
add_volume_attachment="add_volume_attachment"
delete_volume_attachment="delete_volume_attachment"
add_path="add_path"
delete_path="delete_path"
read_volume="read_volume"
read_attachment="read_attachment"
lookup_endpoint="lookup_endpoint"
#Task contents
task_uri="task_uri"
operation_type="operation_type"
object="object"
#other
protocol_uri="https://"
vol_name_prefix="cho_test_vol_"
vol_name_extended_prefix="FT_"
host_endPoint_prefix="00000AA000"
path_in_construction="path_in_construction"
delete_query_param="?force=true"
GB = (1024*1024*1024)
#task status
task_running="Running"
task_completed="Completed"
task_exception="Exception"
task_new="New"
task_updated="Updated"
#volume components
vol_name="name"
vol_pool_id="pool_id"
vol_uri="vol_uri"
#vol attachment components
attachment_vol_uri="attachment_vol_uri"
attachment_paths="attachment_path"
attachment_uri="attachment_uri"
path_host_wwn="path_host_wwn"
path_fc_nw="path_fc_nw"
path_uri="path_uri"
#san-fc mapping components
san_fc_endpoints="endpoints"
#report constants

#task fail constants
fail_keyword="failure"
create_volume_task_fail="create_volume_task_"+fail_keyword
delete_volume_task_fail="delete_volume_task_"+fail_keyword
add_volume_attachment_task_fail="add_attachment_task_"+fail_keyword
delete_volume_attachment_task_fail="delete_attachment_task_"+fail_keyword
add_path_task_fail="add_path_task_"+fail_keyword
missing_added_path_fail="added_path_missing_"+fail_keyword
delete_path_task_fail="delete_path_task_"+fail_keyword
read_volume_fail="read_volume_"+fail_keyword
read_attachment_fail="read_attachment_"+fail_keyword
lookup_endpoint_fail="endpoint_lookup_"+fail_keyword

#request fail constants
create_volume_request_fail="create_volume_request_"+fail_keyword
delete_volume_request_fail="delete_volume_request_"+fail_keyword
add_volume_attachment_request_fail="add_attachment_request_"+fail_keyword
delete_volume_attachment_request_fail="delete_volume_request_"+fail_keyword
add_path_request_fail="add_path_request_"+fail_keyword
delete_path_request_fail="delete_path_request_"+fail_keyword

#task success constants
success_keyword="success"
create_volume_task_success="create_volume_"+ success_keyword
delete_volume_task_success="delete_volume_"+ success_keyword
add_volume_attachment_task_success="add_volume_attachment_"+ success_keyword
delete_volume_attachment_task_success="delete_volume_attachment_"+ success_keyword
add_path_task_success="add_path_"+ success_keyword
delete_path_task_success="delete_path_"+ success_keyword
read_volume_success="read_volume_"+ success_keyword
read_attachment_success="read_attachment_"+ success_keyword
lookup_endpoint_success="endpoint_lookup_"+ success_keyword


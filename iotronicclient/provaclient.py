from iotronicclient import client

kwargs={'os_username': 'admin', 'os_user_domain_name': '', 'os_cacert': None, 'os_tenant_name': 'admin', 'os_user_domain_id': 'default', 'os_iotronic_api_version': None, 'os_password': '<PASSWORD>', 'os_cert': None, 'os_project_id': '', 'retry_interval': 2, 'os_tenant_id': '', 'os_project_name': 'admin', 'os_service_type': '', 'os_key': None, 'os_project_domain_id': 'default', 'insecure': False, 'max_retries': 5, 'os_endpoint_type': '', 'os_region_name': '', 'iotronic_url': '', 'os_auth_url': 'http://controller:35357/v3', 'os_auth_token': '', 'timeout': 600, 'os_project_domain_name': ''}


myclient = client.get_client('1', **kwargs)

print myclient.node.list()
#print myclient.node.get('<resource_id>')




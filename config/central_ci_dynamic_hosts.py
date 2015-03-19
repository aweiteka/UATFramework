#!/usr/bin/python

'''
    Ansible dynamic inventory script for central CI
   returns json of provisioned hosts
'''

import json
import os

resource_file = "resources.json"
# environment variable with path to resource_file
resource_env_var = "OLDPWD"
json_data = None

# If resource_file is not found in current working directory
# try to use the path from resource_env_var
# assumes filename is resource_file in both cases
if not os.path.isfile(resource_file):
    if os.getenv(resource_env_var):
        resource_file = '/'.join([os.getenv(resource_env_var), resource_file])
    else:
        print "Cannot find file '%s' in current working director or env var " \
              "'%s'" % (resource_file, resource_env_var)
        exit(1)

json_data = json.load(open(resource_file))

hosts = {'cihosts': {'hosts': []}}

for host in json_data['resources']:
    if host:
        # Openstack resources
        if 'ip' in host:
            # may need to add user-defined vars here as well. Example:
            # hosts['cihosts']['vars'] = { 'ansible_ssh_user': 'cloud-user'}
            hosts['cihosts']['hosts'].append(host['ip'])
            hosts[host['name']] = [host['ip']]
        # Beaker resources
        if 'system' in host:
            hosts['cihosts']['hosts'].append(host['system'])
            hosts[host['system']] = [host['system']]

print json.dumps(hosts)

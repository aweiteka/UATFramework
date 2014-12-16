#!/usr/bin/python

'''Ansible dynamic inventory script for central CI
   returns json of provisioned hosts'''

import json

resource_file = "resources.json"
json_data = json.load(open(resource_file))

hosts = { 'cihosts': {
          'hosts': []
          }
        }

for host in json_data['resources']:
    if host:
        hosts['cihosts']['hosts'].append(host['ip'])
        # may need to add user-defined vars here as well. Example:
        #hosts['cihosts']['vars'] = { 'ansible_ssh_user': 'cloud-user'}
        hosts[host['name']] = [host['ip']]

print json.dumps(hosts)

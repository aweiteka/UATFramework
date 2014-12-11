'''Magically loaded by behave defining helper methods and other things'''

def before_all(context):
    '''Behave-specific function that runs before anything else'''

    import ConfigParser
    import requests

    config = ConfigParser.ConfigParser()
    config.read('uat.cfg')

    def api(app, path, payload=None, method=None):
        '''Generic interface for making application API calls

        app: match section name of config file

        GET is default
        For POST pass in a payload JSON string
        For DELETE pass in 'method=delete'

        returns JSON results
        '''

        # TODO: support PUT calls
        # TODO: support more auth opts
        AUTH = (config.get(app, 'user'), config.get(app, 'pass'))
        VERIFY = False

        url = '/'.join([config.get(app, 'url'), config.get(app, 'api_path'), path])
        if payload is None:
            if method is None:
                # GET request
                result = requests.get(
                             url,
                             auth=AUTH,
                             verify=VERIFY)
            elif method is "delete":
                # DELETE request
                result = requests.delete(
                             url,
                             auth=AUTH,
                             verify=VERIFY)
        else:
            # POST request
            post_headers = {'content-type': 'application/json'}
            result = requests.post(
                         url,
                         auth=AUTH,
                         verify=VERIFY,
                         headers=post_headers,
                         data=payload)
        if result.raise_for_status():
            print 'Status %s: %s' % (result.status_code, result.json()['error'])
            return False
        if app is "satellite":
            if payload is None and method is None:
                return result.json()['results']
            else:
                return result.json()
        elif app is "openshiftv2":
            print result.json()
            return result.json()

    context.api = api

    def remote_cmd(host, cmd, **kwargs):
        '''Interface to run a command on a remote host using Ansible modules

        host: name of host of remote target system in ansible inventory file
              or environment variable
        cmd: an Ansible module
        module_args: module args in the form of "key1=value1 key2=value2"'''

        import ansible.runner
        import os
        import json

        inventory = None

        if host.isupper():
            # try to match local env var
            # if None then make sure dynamic inventory var is not None
            # then dynamically add list of hosts from dynamic inventory var as a host group

            # dynamic inventory via environment vars
            dynamic_inventory_env_var = config.get('ansible', 'dynamic_inventory_env_var')
            if not os.getenv(dynamic_inventory_env_var):
                print "Environment variable matching '%s' not found" % dynamic_inventory_env_var
                return False
            else:
                dynamic_hosts = os.getenv(dynamic_inventory_env_var)
                inventory_json = json.dumps({ host: [dynamic_hosts] })
                print inventory_json
                inventory = inventory_json
                #inventory = json.loads(inventory_json)
                #inventory = ansible.inventory.Inventory(json.loads(inventory_json))
                print "Environment variable matched '%s', value '%s', but not implemented" % (host, dynamic_hosts)
        else:
            # use inventory file
            inventory = ansible.inventory.Inventory(config.get('ansible', 'inventory'))

        result = ansible.runner.Runner(
                 module_name=cmd,
                 inventory=inventory,
                 pattern=host,
                 sudo=config.get('ansible', 'sudo'),
                 **kwargs
            ).run()

        # TODO support lists of hosts
        if result['dark']:
            print result['dark']
            return False
        elif not result['contacted']:
            print result
            return False
        else:
            for key, val in result['contacted'].iteritems():
                # FIXME: this probably won't work with lists of hosts
                #        one host may fail and another succeed
                if "failed" in val:
                    print val['msg']
                    return False
                else:
                    return val

    context.remote_cmd = remote_cmd

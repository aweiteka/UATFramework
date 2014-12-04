def before_all(context):
    '''Behave-specific function that runs before anything else'''

    import ConfigParser
    import requests
    import json

    config = ConfigParser.ConfigParser()
    config.read('uat.cfg')

    def api(app, path, payload=None, method=None):
        '''Generic interface for making application API calls

        app: match section name of config file

        GET is default
        For POST pass in a payload JSON string
        For DELETE pass in 'method=delete'
        '''

        # TODO: support PUT calls

        AUTH = (config.get(app, 'user'), config.get(app, 'pass'))
        VERIFY = False

        url = '/'.join([config.get(app, 'url'), config.get(app, 'api_path'), path])
        if payload is None:
            if method is None:
                # GET request
                r = requests.get(url,
                                 auth=AUTH,
                                 verify=VERIFY)
            elif method is "delete":
                # DELETE request
                r = requests.delete(url,
                                    auth=AUTH,
                                    verify=VERIFY)
        else:
            # POST request
            post_headers = {'content-type': 'application/json'}
            r = requests.post(url,
                              auth=AUTH,
                              verify=VERIFY,
                              headers=post_headers,
                              data=payload)
        if r.raise_for_status():
            print('Status %s: %s' % (r.status_code, r.json()['error']))
            return False
        if app is "satellite":
            if payload is None and method is None:
                return r.json()['results']
            else:
                return r.json()
        elif app is "openshiftv2":
            print r.json()
            return r.json()

    context.api = api

    def remote_cmd(host, cmd, module_args=None):
        '''Interface to run a command on a remote host using Ansible modules

        host: name of host of remote target system in ansible inventory file
        cmd: an Ansible module
        module_args: module args in the form of "key1=value1 key2=value2"'''

        # FIXME: support kwargs so all module opts can be used

        import ansible.runner

        inventory = ansible.inventory.Inventory(config.get('general', 'ansible_inventory'))

        r = ansible.runner.Runner(
            module_name=cmd,
            module_args=module_args,
            inventory=inventory,
            pattern=host,
        ).run()
        if r['dark']:
            print r['dark'].items()
            return False
        else:
            print r['contacted'].items()
            return True

    context.remote_cmd = remote_cmd

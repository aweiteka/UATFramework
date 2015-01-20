'''Magically loaded by behave defining helper methods and other things'''

# define the necessary logging features to write messages to a file
import logging
from datetime import datetime
import os

if os.getenv("WORKSPACE") is not None:
    logdir = os.getenv("WORKSPACE") + "/logs"
else:
    logdir = "logs"

if not os.path.exists(logdir):
    os.makedirs(logdir)

now_string = datetime.now().strftime('%Y-%b-%d-%H:%M:%S')

logfile = logdir + '/' + now_string + '_behave.log'

file_logger = logging.getLogger()
file_logger.setLevel(logging.INFO)

fh = logging.FileHandler(filename=logfile)
fh.setLevel(logging.INFO)

my_formatter = logging.Formatter('%(asctime)s - %(message)s')

fh.setFormatter(my_formatter)

file_logger.addHandler(fh)

def before_all(context):
    '''Behave-specific function that runs before anything else'''

    import ConfigParser
    import requests

    config = ConfigParser.ConfigParser()
    config.read('config/uat.cfg')

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

    def remote_cmd(cmd, host=None, sudo=None, **kwargs):
        '''Interface to run a command on a remote host using Ansible modules

        host: name of host of remote target system in ansible inventory file
              or environment variable
        cmd: an Ansible module
        module_args: module args in the form of "key1=value1 key2=value2"
        Returns list of values if all hosts successful, otherwise False'''

        import ansible.runner

        inventory = None

        if hasattr(context, 'dynamic_hosts'):
            host = context.dynamic_hosts
            # use custom dynamic hosts script
            inventory = ansible.inventory.Inventory(config.get('ansible', 'dynamic_inventory_script'))
        elif hasattr(context, 'static_host'):
            # use static ansible inventory file
            inventory = ansible.inventory.Inventory(config.get('ansible', 'inventory'))
        else:
            # default to static file
            inventory = ansible.inventory.Inventory(config.get('ansible', 'inventory'))

        # the user can specify to not use 'sudo' per command or use the config file value
        if sudo is not None:
            sudo = sudo
        else:
            sudo = config.get('ansible', 'sudo')

        # the 'context' object can basically hold whatever we want.
        # if we stash the result from Ansible, we can inspect it or log it
        # later
        context.result = ansible.runner.Runner(
                 module_name=cmd,
                 inventory=inventory,
                 pattern=host,
                 sudo=sudo,
                 #remote_user=remote_user,
                 **kwargs
        ).run()

        # TODO support lists of hosts
        if context.result['dark']:
            print context.result['dark']
            return False
        elif not context.result['contacted']:
            print context.result
            return False
        else:
            values = []
            for key, value in context.result['contacted'].iteritems():
                if "failed" in value:
                    return False
                else:
                    values.append(value)
            return values

    context.remote_cmd = remote_cmd

# After each step, we will examine the status and log any results from Ansible
# if they exist
def after_step(context, step):
    if (os.getenv("BEHAVE_DEBUG_LOGGING") is not None
            and os.getenv("BEHAVE_DEBUG_LOGGING") == "True"):
        file_logger.info('Behave Step Name: %s' % step.name)
        file_logger.info('Step Error Message: %s' % step.error_message)
        if hasattr(context, 'result'):
            file_logger.info('Ansible Output: %s' % context.result)
    elif step.status == "failed":
        file_logger.info('Behave Step Name: %s' % step.name)
        file_logger.info('Step Error Message: %s' % step.error_message)
        if hasattr(context, 'result'):
            file_logger.info('Ansible Output: %s' % context.result)


'''test methods for kubernetes'''

import re
from behave import *


@given('"{number}" "{component}" are running')
def step_impl(context, number, component):
    '''check expected number of components are running
       where component is pod, service, node, etc'''
    import json
    r = context.remote_cmd('command',
                            module_args='kubectl get %s -o json' % component)
    if r:
        for i in r:
            data = json.loads(i['stdout'])
            # terrible hack. must be a better way
            if 'items' in data:
                assert len(data['items']) is int(number)
            else:
                assert int(number) is 0
    else:
        assert False

@given('nodes are ready')
def step_impl(context):
    '''check whether the nodes are ready'''
    import json
    r = context.remote_cmd('command', module_args='kubectl get nodes -o json')

    if r:
        for i in r:
            data = json.loads(i['stdout'])
            if 'items' not in data:
                assert True # trivially true
            else:
                # We need to find the Ready condition type and check its status.
                # See docs/admin/node.md#node-condition in kubernetes repo.
                for node in data['items']:
                    for condition in node['status']['conditions']:
                        if condition['type'] == "Ready":
                            assert condition['status'] == 'True'
    else:
        assert False

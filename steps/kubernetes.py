'''test methods for kubernetes'''

import re
import json
from behave import *


def kubectl_get(context, component):

    # NB: Note that we aggregate across masters. This doesn't matter in reality
    # since our cluster test uses only one master. But if we ever change to
    # using multiple masters, things will be different.

    r = context.remote_cmd('command',
                           module_args='kubectl get %s -o json' % component)
    assert r, "unable to get %s" % component

    items = []
    for i in r:
        data = json.loads(i['stdout'])
        if 'items' in data:
            items.extend(data['items'])
    return items


def node_is_ready(node):
    for condition in node['status']['conditions']:
        if condition['type'] == "Ready":
            return condition['status'] == 'True'
    return False


@given('"{number}" "{component}" are running')
def step_impl(context, number, component):
    '''check expected number of components are running
       where component is pod, service, node, etc'''
    assert len(kubectl_get(context, component)) is int(number)

@given('nodes are ready')
def step_impl(context):
    for node in kubectl_get(context, "nodes"):
        assert node_is_ready(node)

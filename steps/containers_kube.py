'''test methods for containers and stuff'''

import re
from behave import *


def get_running_container_id(context):
    '''get running container id'''
    container_result = context.remote_cmd(cmd='command',
                                        module_args='docker ps')

    assert container_result, "Error running 'docker ps'"

    container_re = re.compile(r'^(?P<container>\w{12})'
                              r'\s*(?P<image>[\w:]+)'
                              r'\s*(?P<command>[\w/]+)'
                              r'\s*(?P<created>[\w]+)'
                              r'\s*(?P<status>[\w]+)'
                              r'\s*(?P<ports>[\d]*)'
                              r'\s*(?P<names>[\w_]+)')

    container_id = None
    for item in container_result:
        for l in item['stdout'].split('\n'):
            m = container_re.search(l)
            if m:
                container_id = m.group('container')

    return container_id

def get_images_id(context):
    '''get images id'''
    images_result = context.remote_cmd(cmd='command',
                                       module_args='docker images -q')
    for image in images_result:
        return image['stdout'].split('\n')

@when('docker pull "{image}"')
def step_impl(context, image):
    '''docker pull image'''
    assert context.remote_cmd('command',
                               module_args='docker pull %s' % image)

@then(u'remove docker image "{image}"')
def step_impl(context, image):
    assert context.remote_cmd('command',
                               module_args='docker rmi -f %s' % image)

@then(u'rpm "{rpm}" is installed in "{image}" on "{host}"')
def step_impl(context, rpm, image, host):
    '''docker run and install RPM'''
    assert context.remote_cmd('command',
                               host,
                               module_args='docker run %s yum install -y %s' % (image, rpm))

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

@when('docker stop container')
def step_impl(context):
    '''docker stop container'''
    container_id = get_running_container_id(context)
    assert container_id, "There is not a running container"
    assert context.remote_cmd('command',
                               module_args='docker stop %s' % container_id)

@when('docker run "{image}" detach mode with "{command}"')
def step_impl(context, image, command):
    '''docker run image with detach mode'''
    assert context.remote_cmd('command',
                               module_args='docker run -d %s %s' % (image, command))

@then('check whether there is a running container')
def step_impl(context):
    '''check whether container is running'''
    container_id = get_running_container_id(context)
    assert container_id, "There is not a running container"

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

@when('docker build an image from "{Dockerfile}"')
@when('docker build an image with tag "{tag}" from "{dockerfile}"')
def step_impl(context, dockerfile, tag=''):
    '''Build an image from a Dockerfile'''
    module_args = 'docker build'
    if tag:
        module_args += ' -t %s' % tag
    assert context.remote_cmd('command',
                               module_args='%s %s' % (module_args, dockerfile))

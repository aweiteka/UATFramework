'''test methods for containers and stuff'''

from behave import *

@when('docker pull "{image}"')
def step_impl(context, image):
    '''docker pull image'''
    assert context.remote_cmd('command',
                               remote_user='root',
                               module_args='docker pull %s' % image)

@then(u'remove docker image "{image}"')
def step_impl(context, image):
    assert context.remote_cmd('command',
                               remote_user='root',
                               module_args='docker rmi %s' % image)

@then(u'rpm "{rpm}" is installed in "{image}" on "{host}"')
def step_impl(context, rpm, image, host):
    '''docker run and install RPM'''
    assert context.remote_cmd('command',
                               host,
                               module_args='docker run %s yum install -y %s' % (image, rpm))

@given('"{number}" "{component}" are running')
def step_impl(context, number, component):
    '''check expected number of components are running
       where component is pod, service, minion, etc'''
    import json
    r = context.remote_cmd('command',
                            module_args='kubectl get %s -o json' % component)
    if r:
        for i in r:
            data = json.loads(i['stdout'])
            # terrible hack. must be a better way
            if data['items']:
                assert len(data['items']) is int(number)
            else:
                assert int(number) is 0
    else:
        assert False


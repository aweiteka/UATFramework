'''test methods for containers and stuff'''

from behave import *

@when('image "{image}" is pulled on "{host}"')
def step_impl(context, image, host):
    '''docker pull image'''
    assert context.remote_cmd('command',
                               host,
                               module_args='docker pull %s' % image)

@then(u'rpm "{rpm}" is installed in "{image}" on "{host}"')
def step_impl(context, rpm, image, host):
    '''docker run and install RPM'''
    assert context.remote_cmd('command',
                               host,
                               module_args='docker run %s yum install -y %s' % (image, rpm))

@given('"{number}" pods on "{host}"')
def step_impl(context, number, host):
    '''check expected number of pods'''
    import json
    r = context.remote_cmd('command',
                            host,
                            module_args='kubectl get pods -o json')
    for i in r:
        data = json.loads(i['stdout'])
        # terrible hack. must be a better way
        if data['items']:
            assert len(data['items']) is int(number)
        else:
            assert int(number) is 0

@given('"{number}" services on "{host}"')
def step_impl(context, number, host):
    '''check expected number of services'''
    import json
    r = context.remote_cmd('command',
                            host,
                            module_args='kubectl get services -o json')
    for i in r:
        data = json.loads(i['stdout'])
        # terrible hack. must be a better way
        if data['items']:
            assert len(data['items']) is int(number)
        else:
            assert int(number) is 0

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

@when('application "{app}" is run from "cihosts"')
def step_impl(context, app):
    '''run kubernetes pod'''
    # how do we land the pod/service files?
    assert False

@then('application "{app}" is verified')
def step_impl(context, app):
    '''verify kubernetes app'''
    # TODO: how?
    assert False



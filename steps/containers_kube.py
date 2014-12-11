'''test methods for containers and stuff'''

from behave import *

@when('image "{image}" is pulled')
def step_impl(context, image):
    '''docker pull image'''
    # no 'docker pull' in ansible
    # run from 'command' module?
    assert False

@when('container "{img}" is run on "{host}"')
def step_impl(context, img, host):
    '''run a container'''
    r = context.remote_cmd(host,
                           'docker',
                           module_args='image=%s command=true' % img)
    assert r

@then('"{container}" rpms are updated using host subscription')
def step_impl(context, container):
    '''run yum update -y inside container'''
    assert False

@then('rpm "{rpm}" is installed in "mycontainer"')
def step_impl(context, rpm):
    '''run yum install rpm'''
    assert False

@when('pod "{pod}" is run from "atomic"')
def step_impl(context, pod):
    '''run kubernetes pod'''
    # how do we land the pod/service files?
    assert False

@then('service "{pod}" is verified')
def step_impl(context, pod):
    '''verify kubernetes app'''
    # TODO: how?
    assert True



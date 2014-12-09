'''Common test methods'''

from behave import *

@given(u'"{rpm}" is already installed on "{host}"')
def step_impl(context, rpm, host):
    '''Install RPM on host but fail if not already installed'''
    r = context.remote_cmd(host,
                           "yum",
                           module_args='name=%s' % rpm)
    if r:
        assert r['changed'] is False
    else:
        assert False

@given(u'"{unit}" is already running on "{host}"')
def step_impl(context, unit, host):
    '''Ensure service is running but fail if not'''
    r = context.remote_cmd(host,
                           "service",
                           module_args='name=%s state=running enabled=yes' % unit)
    if r:
        assert r['changed'] is False
    else:
        assert False

@given(u'"{unit}" is started on "{host}"')
def step_impl(context, unit, host):
    '''Start service but fail if already running'''
    r = context.remote_cmd(host,
                           unit,
                           module_args='name=%s state=running enabled=yes' % unit)
    if r:
        assert r['changed'] is True
    else:
        assert False

@given('"{host}" host')
def step(context, host):
    '''Verify we can ping the host

    host: a host from the ansible inventory file'''
    #TODO: if host isupper() pull from env variable
    assert context.remote_cmd(host, 'ping')

@given('run command "{cmd}" on "{host}"')
@when('run command "{cmd}" on "{host}"')
@then('run command "{cmd}" on "{host}"')
def step(context, cmd, host):
    '''Run an Ansible module on a host directly from scenario

    cmd: a module name plus arguments
         <module> key=value [key=value ...]
         or...
         <module> <param>
    host: a host from the inventory file'''
    module, args = None, None
    if ' ' in cmd:
        # we only split on the first space to get the module name
        # since module_args are also space-delimited
        module, args = cmd.split(' ', 1)
    else:
        module = cmd
    assert context.remote_cmd(host,
                              module,
                              module_args=args)

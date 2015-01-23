'''Common test methods'''

from behave import *

@given(u'"{host}" hosts from dynamic inventory')
def step_impl(context, host):
    context.inventory = "dynamic"
    context.target_host = host 

@given(u'"{host}" host from static inventory')
def step_impl(context, host):
    context.inventory = "static"
    context.target_host = host 

@given(u'"{rpm}" is already installed on "{host}"')
def step_impl(context, rpm, host):
    '''Install RPM on host but fail if not already installed'''
    r = context.remote_cmd("yum",
                           host,
                           remote_user="root",
                           module_args='name=%s state=present' % rpm)
    if r:
        for i in r:
            assert i['changed'] is False
    else:
        assert False

@given(u'"{rpm}" is already installed')
def step_impl(context, rpm):
    '''Install RPM on host but fail if not already installed'''
    context.execute_steps(u"""
    given "{package_name}" is already installed on "{host}"
    """.format(package_name=rpm,host=context.target_host))

@given(u'"{rpms}" are already installed on "{host}"')
def step_impl(context, rpms, host):
    '''Install RPM on host but fail if not already installed'''
    r = context.remote_cmd("yum",
                           host,
                           remote_user="root",
                           module_args='name=%s' % rpms)
    if r:
        for i in r:
            assert i['changed'] is False
    else:
        assert False

@given(u'"{rpms}" are already installed')
def step_impl(context, rpms):
    '''Install RPM on host but fail if not already installed'''
    context.execute_steps(u"""
    "given {package_names}" are already installed on "{host}"
    """.format(package_names=rpms,host=context.target_host))

@given(u'"{unit}" is already running on "{host}"')
def step_impl(context, unit, host):
    '''Ensure service is running but fail if not'''
    r = context.remote_cmd("service",
                           host,
                           module_args='name=%s state=running enabled=yes' % unit)
    if r:
        for i in r:
            assert i['changed'] is False
    else:
        assert False

@then(u'"{unit}" is started and enabled on "{host}"')
def step_impl(context, unit, host):
    '''Start service but fail if already running'''
    r = context.remote_cmd('service',
                           host,
                           module_args='name=%s state=running enabled=yes' % unit)
    if r:
        for i in r:
            assert i['changed'] is True
    else:
        assert False

@given('"{host}" host')
def step(context, host):
    '''Verify we can ping the host

    host: a host from the ansible inventory file'''
    assert context.remote_cmd('ping', host)

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
    assert context.remote_cmd(module,
                              host,
                              module_args=args)

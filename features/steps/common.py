from behave import *

@given('"{host}" host')
def step(context, host):
    '''Verify we can reach the host

    host: a host from the ansible inventory file'''
    assert context.remote_cmd('ping', host)

@given('run command "{cmd}" on "{host}"')
@when('run command "{cmd}" on "{host}"')
@then('run command "{cmd}" on "{host}"')
def step(context, cmd, host):
    '''Run an Ansible module on a host

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

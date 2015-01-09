'''ostree test methods'''

import time
from behave import *

@given(u'active tree version is at "{version}" on "{host}"')
@then(u'active tree version is at "{version}" on "{host}"')
def step_impl(context, version, host):
    '''Get the active version of the tree installed'''
    version_result = context.remote_cmd(cmd='command',
                                        host=host,
                                        sudo=False,
                                        module_args='atomic status')

    # remote_cmd returns a list, so iterate through the list looking for the
    # particular version string
    if version_result:
        for item in version_result:
            assert ("* %s" % version) in item['stdout']

@when(u'atomic "{atomic_cmd}" is run on "{host}"')
def step_impl(context, atomic_cmd, host):
    '''Run atomic command'''
    atomic_result = context.remote_cmd(cmd='command',
                                       host=host,
                                       module_args='atomic %s' % atomic_cmd)

    assert atomic_result

@then(u'wait "{seconds}" seconds for "{host}" to reboot')
def step_impl(context, seconds, host):
    '''Reboot a host and wait a specified time for it to come back'''
    # Arguably, this step can probably be done more elegantly, but right now
    # this works just fine.
    reboot_result = context.remote_cmd(cmd='command',
                                       host=host, 
                                       module_args='systemctl reboot',
                                       module_vars={'async': 0, 'poll': 0, 'ignore_errors': True})

    time.sleep(float(seconds))
    ping_result = context.remote_cmd(cmd='ping', 
                                     host=host,
                                     sudo=False)
    assert ping_result

'''ostree test methods'''

import re
import time
from behave import *


@given(u'active tree version is at "{version}" on "{host}"')
@then(u'active tree version is at "{version}" on "{host}"')
def step_impl(context, version, host):
    '''Get the active version of the tree installed'''
    version_result = context.remote_cmd(cmd='command',
                                        host=host,
                                        sudo=False,
                                        module_args='atomic host status')

    assert version_result

    # gnarly regex to search through the active version line
    status_re = re.compile(r'^\* '
                           r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
                           r' {5}(?P<version>\d+.\d+.\d+)'
                           r' {5}(?P<id>\w{10})'
                           r' {5}(?P<osname>[\w\-]+)'
                           r' {5}(?P<refspec>[\w:\-/]+)')

    # parsing the output for the version number
    active_version = None
    for item in version_result:
        for l in item['stdout'].split('\n'):
            m = status_re.search(l)
            if m:
                active_version = m.group('version')

    assert active_version == version


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
                                       module_vars={'async': 0,
                                                    'poll': 0,
                                                    'ignore_errors': True})

    time.sleep(float(seconds))
    ping_result = context.remote_cmd(cmd='ping',
                                     host=host,
                                     sudo=False)
    assert ping_result


@when(u'"{src_file}" is copied to "{dest_file}"')
def step_imp(context, src_file, dest_file):
    # Copy a file to a destination file on a remote host
    # Currently defaults to 0744 for permissions
    copy_result = context.remote_cmd(cmd='copy',
                                     module_args='src=%s dest=%s mode=0744' %
                                                 (src_file, dest_file))

    assert copy_result


@when(u'"{script}" is executed')
def step_impl(context, script):
    # Execute a script (any file really) on the remote host
    exec_result = context.remote_cmd(cmd='command',
                                     module_args=script)

    assert exec_result


@then(u'"{remote_file}" is fetched to "{local_dir}"')
def step_impl(context, remote_file, local_dir):
    # Retrieve a remote file to a local directory
    fetch_result = context.remote_cmd(cmd='fetch',
                                      module_args='src=%s dest=%s flat=yes' %
                                                  (remote_file, local_dir))

    assert fetch_result


@then(u'atomic host upgrade should return an unregistered error')
def step_impl(context):
    expected_err = ("error: origin unconfigured-state: This system is not " +
                    "registered to Red Hat Subscription Management. You " +
                    "can use subscription-manager to register.")

    upgrade_result = context.remote_cmd(cmd='command',
                                        ignore_rc=True,
                                        sudo=True,
                                        module_args='atomic host upgrade')

    for r in upgrade_result:
        assert expected_err in r['stderr']


@given(u'there is "{num}" atomic host tree deployment')
@then(u'there is "{num}" atomic host tree deployment')
def step_impl(context, num):
    status_result = context.remote_cmd(cmd='command',
                                       module_args='atomic host status')

    assert status_result

    for r in status_result:
        assert len(r['stdout'].split('\n')) == int(num) + 1


@then(u'atomic host rollback should return a deployment error')
def step_impl(context):
    expected_err = ("error: Found 1 deployments, at least 2 required " +
                    "for rollback")

    rollback_result = context.remote_cmd(cmd='command',
                                         ignore_rc=True,
                                         sudo=True,
                                         module_args='atomic host rollback')

    for r in rollback_result:
        assert expected_err in r['stderr']


@then(u'atomic host upgrade reports no upgrade available')
def step_impl(context):
    expected_msg = "No upgrade available."

    upgrade_result = context.remote_cmd(cmd='command',
                                        sudo=True,
                                        module_args='atomic host upgrade')

    assert upgrade_result

    for r in upgrade_result:
        assert expected_msg in r['stdout']

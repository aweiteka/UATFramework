'''ostree test methods'''

import os
import re
import time
import filecmp
from behave import *
from containers_kube import get_images_id, get_running_container_id


def get_atomic_version(context):
    version_result = context.remote_cmd(cmd='command',
                                        module_args='atomic host status')

    assert version_result, "Error running 'atomic host status'"

    status_re = re.compile(r'^\* '
                           r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
                           r' {5}(?P<version>\S+)'
                           r' +(?P<id>\w{10})'
                           r' {5}(?P<osname>[\w\-]+)'
                           r' {5}(?P<refspec>[\w:\-/]+)')

    atomic_version = None
    for item in version_result:
        for l in item['stdout'].split('\n'):
            m = status_re.search(l)
            if m:
                atomic_version = m.group('version')

    return atomic_version


def find_mount_point(context, mountpoint):
    '''Find atomic mount point'''
    filter_str = "mount | grep -E '/dev/mapper/atomic-\w{64}-\w{6}\son\s%s'" % mountpoint
    filter_result = context.remote_cmd(cmd='shell',
                                       module_args=filter_str)
    return filter_result


@given(u'active tree version is at "{version}" on "{host}"')
@then(u'active tree version is at "{version}" on "{host}"')
def step_impl(context, version, host):
    '''Get the active version of the tree installed'''

    atomic_version = get_atomic_version(context)
    assert atomic_version == version, \
        ("The current atomic version %s " % atomic_version +
         "does not match the expected version %s" % version)


@when(u'atomic "{atomic_cmd}" is run on "{host}"')
def step_impl(context, atomic_cmd, host):
    '''Run atomic command'''
    atomic_result = context.remote_cmd(cmd='command',
                                       host=host,
                                       module_args='atomic %s' % atomic_cmd)

    assert atomic_result, "Error running 'atomic %s'" % atomic_cmd


@then(u'wait "{seconds}" seconds for "{host}" to reboot')
@when(u'wait "{seconds}" seconds for "{host}" to reboot')
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
                                     host=host)
    assert ping_result, "Unable to ping host after reboot"


@when(u'"{src_file}" is copied to "{dest_file}"')
def step_imp(context, src_file, dest_file):
    # Copy a file to a destination file on a remote host
    # Currently defaults to 0744 for permissions
    copy_result = context.remote_cmd(cmd='copy',
                                     module_args='src=%s dest=%s mode=0744' %
                                                 (src_file, dest_file))

    assert copy_result, \
        ("Error copying local file %s to remote destination %s" %
         (src_file, dest_file))


@when(u'the script named "{script}" is executed')
def step_impl(context, script):
    # Execute a script (any file really) on the remote host
    exec_result = context.remote_cmd(cmd='command',
                                     module_args=script)

    assert exec_result, "Error executing script named %s" % script


@then(u'"{remote_file}" is fetched to "{local_dir}"')
def step_impl(context, remote_file, local_dir):
    # Retrieve a remote file to a local directory
    fetch_result = context.remote_cmd(cmd='fetch',
                                      module_args='src=%s dest=%s flat=yes' %
                                                  (remote_file, local_dir))

    assert fetch_result, \
        ("Error fetching remote file %s to local directory %s" %
         (remote_file, local_dir))


@then(u'atomic host upgrade should return an unregistered error')
def step_impl(context):
    expected_err = ("error: origin unconfigured-state: This system is not " +
                    "registered to Red Hat Subscription Management. You " +
                    "can use subscription-manager to register.")

    upgrade_result = context.remote_cmd(cmd='command',
                                        ignore_rc=True,
                                        module_args='atomic host upgrade')

    for r in upgrade_result:
        assert expected_err in r['stderr'], \
            ("Did not receive the expected error when running " +
             "'atomic host upgrade'")


@given(u'there is "{num}" atomic host tree deployed')
@then(u'there is "{num}" atomic host tree deployed')
def step_impl(context, num):
    status_result = context.remote_cmd(cmd='command',
                                       module_args='atomic host status')

    assert status_result, "Error running 'atomic host status'"

    for r in status_result:
        assert len(r['stdout'].split('\n')) == int(num) + 1, \
            "Did not find the expected number of deployments (%s)" % num


@then(u'atomic host rollback should return a deployment error')
def step_impl(context):
    expected_err = ("error: Found 1 deployments, at least 2 required " +
                    "for rollback")

    rollback_result = context.remote_cmd(cmd='command',
                                         ignore_rc=True,
                                         module_args='atomic host rollback')

    for r in rollback_result:
        assert expected_err in r['stderr'], \
            ("Did not receive the expected error when running " +
             "'atomic host rollback")


@then(u'atomic host upgrade reports no upgrade available')
def step_impl(context):
    expected_msg = "No upgrade available."

    upgrade_result = context.remote_cmd(cmd='command',
                                        module_args='atomic host upgrade')

    assert upgrade_result, "Error while running 'atomic host upgrade'"

    for r in upgrade_result:
        assert expected_msg in r['stdout'], \
            ("Did not receive the expected error when running " +
             "'atomic host upgrade'")


@given(u'the original atomic version has been recorded')
def step_impl(context):
    context.original_version = get_atomic_version(context)
    assert context.original_version is not None, \
        "Unable to record the current atomic version"


@then(u'the current atomic version should match the original atomic version')
def step_impl(context):
    current_version = get_atomic_version(context)
    assert current_version is not None, \
        "Unable to retrieve the current atomic version"
    assert current_version == context.original_version, \
        ("The current atomic version %s " % current_version +
         "did not match the original atomic version " +
         "%s" % context.original_version)


@given(u'machine-id on "{host}" is recorded')
def step_impl(context, host):
    context.machine_id = context.remote_cmd(cmd='command',
                                            host=host,
                                            module_args='cat /etc/machine-id')[0]['stdout']
    assert context.machine_id is not None, \
        "Unable to read /etc/machine-id"
    fd = open('/tmp/' + host, 'w')
    fd.write(context.machine_id)
    fd.close()


@then(u'check if the machine-id on "{host1}" and "{host2}" differ')
def step_impl(context, host1, host2):
    machine_ids_equal = filecmp.cmp('/tmp/' + host1, '/tmp/' + host2)
    assert machine_ids_equal is True, \
        "Test failed. /etc/machine-id are equal."


@when(u'atomic host upgrade is successful')
def step_impl(context):
    upgrade_result = context.remote_cmd(cmd='command',
                                        module_args='atomic host upgrade')

    assert upgrade_result, "Error performing 'atomic host upgrade"


@then(u'the current atomic version should not match the original atomic version')
def step_impl(context):
    current_version = get_atomic_version(context)
    assert current_version is not None, \
        "Unable to retrieve the current atomic version"
    assert current_version != context.original_version, \
        ("The current atomic version %s " % current_version +
         "erroneously matched the original atomic version " +
         "%s" % context.original_version)


@when(u'atomic host rollback is successful')
def step_impl(context):
    rollback_result = context.remote_cmd(cmd='command',
                                         module_args='atomic host rollback')

    assert rollback_result, "Error while running 'atomic host rollback'"


@given(u'the data collection script is present')
def step_impl(context):
    stat_result = context.remote_cmd(cmd='stat',
                                     module_args='path=/usr/local/bin/atomic_smoketest.sh')

    assert stat_result, "The data collection script is missing"


@when(u'the data collection script is run')
def step_impl(context):
    run_result = context.remote_cmd(cmd='command',
                                    module_args='/usr/local/bin/atomic_smoketest.sh')

    assert run_result, "Error while running data collection script"


@then(u'the data collection output file is present')
def step_impl(context):
    stat_result = context.remote_cmd(cmd='stat',
                                     module_args='path=/var/qe/atomic_smoke_output.txt')

    assert stat_result, "The data collection output file is missing"


@then(u'the data collection output files are retrieved')
def step_impl(context):
    jenkins_ws = os.getenv('WORKSPACE')
    fetch_result = context.remote_cmd(cmd='fetch',
                                      module_args='src=/var/qe/atomic_smoke_output.txt dest=%s/ flat=yes' % jenkins_ws)

    assert fetch_result, "Error retrieving the data collection output file"

    fetch_result = context.remote_cmd(cmd='fetch',
                                      module_args='src=/var/qe/atomic_smoke_failed dest=%s/ flat=yes' % jenkins_ws)

    assert fetch_result, "Error retrieving the data collection failure file"


@given(u'the upgrade interrupt script is present')
def step_impl(context):
    stat_result = context.remote_cmd(cmd='stat',
                                     module_args='path=/usr/local/bin/atomic_upgrade_interrupt.sh')

    assert stat_result, "The atomic upgrade interrupt script is missing"


@when(u'the upgrade interrupt script is run "{num}" times')
def step_impl(context, num):
    int_result = context.remote_cmd(cmd='command',
                                    module_args='/usr/local/bin/atomic_upgrade_interrupt.sh %s' % num)

    assert int_result, "Error while running atomic upgrade interrupt script"


@given(u'the rollback interrupt script is present')
def step_impl(context):
    stat_result = context.remote_cmd(cmd='stat',
                                     module_args='path=/usr/local/bin/atomic_rollback_interrupt.sh')

    assert stat_result, "The atomic rollback interrupt script is missing"


@when(u'the rollback interrupt script is run "{num}" times')
def step_impl(context, num):
    int_result = context.remote_cmd(cmd='command',
                                    module_args='/usr/local/bin/atomic_rollback_interrupt.sh %s' % num)

    assert int_result, "Error while running atomic rollback interrupt script"


@when(u'rollback and reboot occurs multiple times')
def step_impl(context):
    for l in range(9):
        context.execute_steps(u'''
            Given the original atomic version has been recorded
             When atomic host rollback is successful
              and wait "30" seconds for "all" to reboot
             Then the current atomic version should not match the original atomic version
        ''')


@when(u'rollback occurs multiple times')
def step_impl(context):
    for l in range(10):
            context.execute_steps(u'''
                When atomic host rollback is successful
            ''')


@when('atomic stop container')
def step_impl(context):
    '''stop running container'''
    container_id = get_running_container_id(context)
    assert container_id, "No running container"
    assert context.remote_cmd('command',
                               module_args='atomic stop %s' % container_id)


@when(u'atomic mount "{container_or_image}" to a specified "{mountpoint}"')
def step_impl(context, container_or_image, mountpoint):
    '''mount container or image to a specified directory'''
    container_or_image_id = None
    if container_or_image == "container":
        container_or_image_id = get_running_container_id(context)
        assert container_or_image_id, "No running container"

    if container_or_image == "image":
        container_or_image_id = get_images_id(context)[0]
        assert container_or_image_id, "No available image"

    mount_result = context.remote_cmd(cmd='command',
                                      module_args='atomic mount %s '
                                                  '%s' % (container_or_image_id,
                                                          mountpoint))

    assert mount_result is not None, "Error while running 'atomic mount'"


@then(u'check whether atomic mount point "{mountpoint}" exists')
def step_impl(context, mountpoint):
    '''check whether atomic mount point exists'''
    filter_result = find_mount_point(context, mountpoint)
    assert filter_result, "Error while finding mounted container"


@when(u'atomic unmount image from previous "{mountpoint}"')
@when(u'atomic unmount container from previous "{mountpoint}"')
def step_impl(context, mountpoint):
    '''unmount container or image from previous mounted directory'''
    unmount_result = context.remote_cmd(cmd='command',
                                        module_args='atomic unmount %s' % mountpoint)

    assert unmount_result, "Error while running 'atomic unmount'"


@then(u'check whether atomic mount point "{mountpoint}" does not exist')
def step_impl(context, mountpoint):
    '''check whether atomic mount point does not exist'''
    filter_result = find_mount_point(context, mountpoint)
    assert filter_result is not None, "Error unmounted container still exists"

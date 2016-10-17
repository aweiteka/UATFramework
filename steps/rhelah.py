'''ostree test methods'''

import os
import re
import time
import filecmp
from behave import *
from distutils.version import LooseVersion
from docker import get_image_id_by_name, get_running_container_id, string_to_bool
from ostree import get_ostree_admin_status


def get_atomic_version(context):
    atomic_status = get_atomic_status(context)
    atomic_version = ""
    for item in atomic_status:
        if item['selected']:
            atomic_version = item['version']
            break

    return atomic_version

def get_atomic_status(context):
    status_result = context.remote_cmd(cmd='command',
                                       module_args='atomic host status')

    assert status_result, "Error running 'atomic host status'"


    status_re = re.compile(r'(?P<timestamp>.*?\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})'
                           r' {5}(?P<version>\S+)'
                           r' +(?P<id>\w{10})'
                           r' {5}(?P<osname>[\w\-]+)'
                           r' {5}(?P<refspec>[\w:\-/]+)')

    atomic_host_status = []
    context.atomic_host_status = ""
    for item in status_result:
        context.atomic_host_status += item['stdout']
        for l in item['stdout'].split('\n'):
            tmp = status_re.search(l)
            if tmp:
                tmp_dict = tmp.groupdict()
                timestamp = tmp_dict['timestamp']
                if re.match("\*", timestamp):
                    tmp_dict['selected'] = True
                    tmp_dict['timestamp'] = re.findall('\*\s+(.*)',
                                                       timestamp)[0]
                else:
                    tmp_dict['selected'] = False
                    tmp_dict['timestamp'] = timestamp.strip()
                atomic_host_status.append(tmp_dict)

    return atomic_host_status


def is_select_old_version(context):
    atomic_status = get_atomic_status(context)
    time_format = '%Y-%m-%d %H:%M:%S'

    for item in atomic_status:
        if item['selected']:
            current_version = LooseVersion(item['version'])
            current_timestamp = time.strptime(item['timestamp'], time_format)
        else:
            another_version = LooseVersion(item['version'])
            another_timestamp = time.strptime(item['timestamp'], time_format)

    if current_version < another_version:
        return True
    if current_version == another_version:
        if current_timestamp < another_timestamp:
            return True

    return False


def get_atomic_host_tree_num(context):
    return len(get_atomic_status(context))


def find_mount_option(context, mount_option):
    '''Find mount option'''
    filter_str = "grep -E '%s' /proc/mounts" % mount_option
    filter_result = context.remote_cmd(cmd='shell',
                                       module_args=filter_str)
    return filter_result


def get_images(context):
    '''Get all installed container images on your system'''
    images_result = context.remote_cmd(cmd='command',
                                       module_args='atomic images list')
    assert images_result, "Error while running 'atomic images'"
    return images_result[0]['stdout'].splitlines()


def get_specified_image(context, image, images_info):
    '''Get specified image on your system'''
    find_image = None
    # Only show images line
    real_images = images_info[1:]
    if not real_images:
        return find_image

    for image_line in real_images:
        find_image = re.findall(image, image_line)
        if find_image:
            break
    return find_image


def get_atomic_image_id_by_name(context, image_name):
    '''Get atomic image id by name'''
    image_id = get_image_id_by_name(context, image_name)
    if image_id:
        image_id = 'sha256:' + image_id

    return image_id


def get_image_label(context, image, target='local'):
    '''Display label information about an image'''
    module_args = 'atomic info'
    if target == 'remote':
        module_args += ' --%s' % target
    label_result = context.remote_cmd(cmd='command',
                                      module_args='%s %s' % (module_args, image))
    return label_result


def get_scanners(context):
    '''Get available scanners'''
    scanners = context.remote_cmd(cmd='command',
                                  module_args='atomic scan --list')
    assert not scanners is False, context.result['contacted']
    return scanners[0]['stdout']


def atomic_scanner(context, target, scanner, scan_type, options):
    '''Scan images or containers or all'''
    options = '--scanner %s --scan_type %s %s' % (scanner, scan_type, options)
    scan_result = context.remote_cmd(cmd='command',
                                     module_args='atomic scan %s %s' % (target, options))
    assert not scan_result is False, context.result['contacted']
    return scan_result[0]['stdout']


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
    start_time = time.time()
    reboot_result = context.remote_cmd(cmd='command',
                                       host=host,
                                       module_args='systemctl reboot',
                                       module_vars={'async': 0,
                                                    'poll': 0,
                                                    'ignore_errors': True})

    time.sleep(float(seconds))
    end_time = time.time()

    uptime_result = context.remote_cmd(cmd='command', host=host,
                                       module_args='cat /proc/uptime')

    if uptime_result:
        uptime = uptime_result[0]['stdout'].split()[0]

        assert float(uptime) < end_time - start_time, \
               "Host not reboot at all"

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
    context.ah_tree_num = get_atomic_host_tree_num(context)
    assert context.ah_tree_num == int(num), \
            "Did not find the expected number of deployments (%s)" % num


@given(u'get the number of atomic host tree deployed')
def step_impl(context):
    context.ah_tree_num = get_atomic_host_tree_num(context)


@when(u'confirm atomic host tree to old version')
def step_impl(context):
    if context.ah_tree_num == 2 and not is_select_old_version(context):
        context.execute_steps(u'''
            When atomic host rollback is successful
            Then wait "30" seconds for "all" to reboot
        ''')


    assert context.ah_tree_num == 1 or is_select_old_version(context), \
           ("Atomic host tree deployed in a new version. "
            "Current status is:\n%s" % context.atomic_host_status)

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

    for r in upgrade_result:
        assert "No upgrade available" not in r['stdout'], \
            "Upgrade is unexpectedly not available"

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


@then(u'the generated data files are retrieved')
def step_impl(context):
    jenkins_ws = os.getenv('WORKSPACE')

    stat_result = context.remote_cmd(cmd='stat',
                                     module_args='path=/var/qe/atomic_smoke_output.txt')

    assert stat_result, "The data collection output file is missing"

    fetch_result = context.remote_cmd(cmd='fetch',
                                      module_args='src=/var/qe/atomic_smoke_output.txt dest=%s/ flat=yes' % jenkins_ws)

    assert fetch_result, "Error retrieving smoketest output"

    stat_result = context.remote_cmd(cmd='stat',
                                     module_args='path=/var/qe/atomic_version.txt')

    assert stat_result, "The atomic version file is missing"

    fetch_result = context.remote_cmd(cmd='fetch',
                                      module_args='src=/var/qe/atomic_version.txt dest=%s/ flat=yes' % jenkins_ws)

    assert fetch_result, "Error retrieving atomic version file"

    fetch_result = context.remote_cmd(cmd='fetch',
                                      module_args='src=/var/qe/atomic_smoke_failed dest=%s/ flat=yes' % jenkins_ws)

    assert fetch_result, "Error retrieving smoketest failure output"


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
@when('atomic stop container "{name}"')
def step_impl(context, name=None):
    '''stop running container'''
    container = None
    if name is not None:
        container = name
    else:
        container = get_running_container_id(context)
    assert container, "No running container"
    assert context.remote_cmd('command',
                              module_args='atomic stop %s' % container)


@when(u'atomic mount image "{name}" to a specified "{mount_option}"')
@when(u'atomic mount image "{name}" with "{option}" to a specified "{mount_option}"')
def step_impl(context, name, mount_option, ignore_rc=False, option=""):
    '''mount image to a specified directory'''
    args = "%s %s %s" % (option, name, mount_option)
    if option == "--live":
        ignore_rc = True

    mount_result = context.remote_cmd(cmd='command',
                                      ignore_rc=ignore_rc,
                                      module_args='atomic mount %s' % args)

    if option == "--live":
        assert 'non-running' in mount_result[0]['stderr'], "Error can mount image with %s" % option
    else:
        assert mount_result is not None, "Failed to mount image '%s'" % name


@when(u'atomic mount container "{name}" to a specified "{mount_option}"')
@when(u'atomic mount container "{name}" with "{option}" to a specified "{mount_option}"')
def step_impl(context, name, mount_option, option=""):
    '''mount container to a specified directory'''
    args = "%s %s %s" % (option, name, mount_option)
    mount_result = context.remote_cmd(cmd='command',
                                      module_args='atomic mount %s' % args)

    assert mount_result is not None, "Failed to mount container '%s'" % name


@then(u'check whether mount option "{mount_option}" exists')
def step_impl(context, mount_option):
    '''check whether mount option exists'''
    filter_result = find_mount_option(context, mount_option)
    assert filter_result, "Error while finding mount option %s" % mount_option


@when(u'atomic unmount image from previous "{mount_option}"')
@when(u'atomic unmount container from previous "{mount_option}"')
def step_impl(context, mount_option):
    '''unmount container or image from previous mounted directory'''
    unmount_result = context.remote_cmd(cmd='command',
                                        module_args='atomic unmount %s' % mount_option)

    assert unmount_result, "Error while running 'atomic unmount'"


@then(u'check whether "{mount_option}" does not exist')
@then(u'check whether mount option "{mount_option}" does not exist')
def step_impl(context, mount_option):
    '''check whether mount option does not exist'''
    filter_result = find_mount_option(context, mount_option)
    assert filter_result is not None, "Error mount option %s still exists" % mount_option

@when(u'atomic update latest "{image}" from repository')
def step_impl(context, image):
    '''Pull latest image from repository'''
    update_result = context.remote_cmd(cmd='command',
                                       module_args='atomic update %s' % image)

    assert update_result, "Error while running 'atomic update'"


@then(u'check whether "{image}" is installed')
def step_impl(context, image):
    '''Check whether specified image is installed on your system'''
    images_info = get_images(context)
    find_result = get_specified_image(context, image, images_info)

    assert find_result, "Error can't find specified image on the system"


@when(u'Remove "{container_or_image}" from system')
def step_impl(context, container_or_image):
    '''Remove container or image from system'''
    assert context.remote_cmd(cmd='command',
                              module_args='atomic uninstall %s' % container_or_image)


@then(u'Check whether "{image}" is removed from system')
def step_impl(context, image):
    '''Check whether specified image is removed from system'''
    images_info = get_images(context)
    find_result = get_specified_image(context, image, images_info)

    assert not find_result, "Error still can find specified image on the system"


@given(u'List all locally installed container images')
@when(u'List all locally installed container images')
def step_impl(context):
    '''List all installed container images on your system'''
    assert get_images(context)


@then(u'Check whether dangling images exist')
def step_impl(context):
    '''Check whether specified image is installed on your system'''
    images_info = get_images(context)
    find_result = get_specified_image(context, '\*\s+<none>', images_info)

    assert find_result, "Error can't find dangling images on the system"


@when(u'Remove all dangling images')
def step_impl(context):
    '''Remove all dangling images on your system'''
    assert context.remote_cmd(cmd='command',
                              module_args='atomic images prune')


@then(u'Check whether dangling images do not exist')
def step_impl(context):
    '''Check whether dangling images are removed from your system'''
    images_info = get_images(context)
    find_result = get_specified_image(context, '\*\s+<none>', images_info)

    assert not find_result, "Error still can find dangling images on the system"


@when(u'"{list_type}" RPM list is collected')
def step_impl(context, list_type):
    ver_res = context.remote_cmd(cmd='shell',
                                 module_args="atomic host status | grep \* | awk '{print $4}' > /var/qe/%s_atomic_version" % list_type)

    assert ver_res, "Error determining atomic host version"

    rpm_list_res = context.remote_cmd(cmd='shell',
                                      module_args='rpm -qa | sort > /var/qe/%s_rpm_list' %
                                      list_type)

    assert rpm_list_res, "Error retrieving list of installed RPMs"


@then(u'the text file with the "{list_type}" RPM list is retrieved')
def step_impl(context, list_type):
    jenkins_ws = os.getenv('WORKSPACE')
    file_res = context.remote_cmd(cmd='stat',
                                  module_args='path=/var/qe/%s_rpm_list' % list_type)

    assert file_res, "The text file with the %s RPM list was not present" % list_type

    file_res = context.remote_cmd(cmd='stat',
                                  module_args='path=/var/qe/%s_atomic_version' % list_type)

    assert file_res, "The text file with the %s atomic verstion was not present" % list_type

    fetch_result = context.remote_cmd(cmd='fetch',
                                      module_args='src=/var/qe/%s_rpm_list dest=%s/ flat=yes' % (list_type, jenkins_ws))

    assert fetch_result, "Error retrieving %s RPM list" % list_type

    fetch_result = context.remote_cmd(cmd='fetch',
                                      module_args='src=/var/qe/%s_atomic_version dest=%s/ flat=yes' % (list_type, jenkins_ws))

    assert fetch_result, "Error retrieving %s atomic version file"


@when(u'Display LABEL information about an image "{image}"')
@when(u'Display LABEL information about a "{target}" image "{image}"')
def step_impl(context, image, target='local'):
    '''Display label information about an image'''
    label_result = get_image_label(context, image, target)
    for label in label_result:
        context.current_label = label['stdout'].splitlines()


@then(u'Check LABEL "{label}" information for an image')
def step_impl(context, label):
    '''Check label information for an image'''
    assert label in context.current_label, "The current label information \
                                            doesn't match with setting"


@when(u'Display "{image}" "{label}" of name version release')
def step_impl(context, image, label=''):
    '''Display image label of name version release'''
    image_info = context.remote_cmd(cmd='command',
                                    module_args='atomic version %s' % image)
    if not label:
        assert image_info, "Error can not get image info"
    else:
        assert label in image_info[0]['stdout'], \
            ("The given LABEL value %s in %s " % (label, image) +
             "does not match the current LABEL value in %s" % image_info)


@when(u'Execute "{image}" install method')
@when(u'Execute "{image}" install method with "{arguments}"')
def step_impl(context, image, arguments=''):
    '''Execute image install method'''
    assert context.remote_cmd(cmd='command',
                              module_args='atomic install %s %s' % (image, arguments))


@when(u'Read the LABEL INSTALL field in the container "{image}"')
@when(u'Read the LABEL INSTALL "{label}" field in the container "{image}"')
def step_impl(context, image, label=''):
    '''Check LABEL INSTALL in the image'''
    install_label = context.remote_cmd(cmd='command',
                                       module_args='atomic install %s' % image)
    if not label:
        assert install_label, "Error can not get LABEL INSTALL in the image"
    else:
        assert label in install_label[0]['stdout'], \
            ("The current LABEL INSTALL %s " % install_label +
             "does not match the expected LABEL INSTALL %s" % label)


@when(u'Compare the RPMs between "{imageA}" and "{imageB}"')
@when(u'Compare the RPMs with "{arguments}" between "{imageA}" and "{imageB}"')
@when(u'Compare the RPMs between "{imageA}" and "{imageB}" are "{rpms}" RPMs based')
def step_impl(context, imageA, imageB, rpms='yes', arguments=''):
    '''Compare the RPMs found in two different images or containers'''
    options = arguments + ' ' + imageA + ' ' + imageB
    result = context.remote_cmd(cmd='command',
                                module_args='atomic diff %s' % options)
    same_image_msg = "The %s is the same to %s!!" % (imageA, imageB)
    diff_image_msg = "The %s is different from %s!!" % (imageA, imageB)

    if rpms == 'no':
        assert "not RPM based" not in result, "The image is not RPM based!!"

    if rpms == 'yes' and imageA != imageB:
        assert result, diff_image_msg
    else:
        if 'r' in arguments and 'json' not in arguments:
            assert "have no different RPMs" not in result, same_image_msg
        elif 'n' not in arguments or arguments == '' and 'json' not in arguments:
            assert "no file differences" not in result, same_image_msg
        else:
            assert result, diff_image_msg


@when(u'List default scanners')
@when(u'List available scanners')
def step_impl(context):
    '''List available scanners'''
    scanners = get_scanners(context)
    assert scanners, "Error can not list available scanners"


@then(u'Find specified scanner "{scanner}"')
def step_impl(context, scanner):
    '''Find specified scanner'''
    scanners = get_scanners(context)
    assert scanner in scanners, "Can't find scanner '%s'" % scanner


@when(u'Scan "{target}"')
@when(u'Scan "{target}" with "{scanner}"')
@when(u'Scan "{target}" with "{scanner}" and "{scan_type}"')
@when(u'Scan "{target}" with "{scanner}" and "{scan_type}" "{options}"')
def step_impl(context, target, scanner='openscap', scan_type='cve',
              options='--verbose'):
    '''Scan images or/and containers with scanner and scan type'''
    scan_result = atomic_scanner(context, target, scanner, scan_type, options)
    context.scan_result = scan_result
    context.scan_type = scan_type

    assert context.scan_result, "Error can't run atomic scan"


@then(u'Check "{matches}" in scanner report')
def step_impl(context, matches):
    '''Check scanner result'''
    result = context.scan_result
    scan_type = context.scan_type
    output = "Find '%s' in scanner report" % matches
    if 'issues were found' in matches:
        assert matches not in result, "Please file a '%s' type bug" % scan_type

    elif 'not supported' in matches:
        assert matches in result, "the image is not supported for this scan"

    else:
        assert matches not in result, output

@then(u'check "{container}" "{mount_option}"')
@then(u'check "{container}" "{mount_option}" "{option}"')
def step_impl(context, container, mount_option, option=None):
    '''Check mount point permission in the container'''
    matches = ""
    result = ""
    expected_output = "Read-only"
    target_file = os.path.join('%s' % mount_option, 'tmp/test')
    mkfile = context.remote_cmd('file',
                                module_args='path=%s state=touch' % target_file)
    if not option:
        result = mkfile[0]['msg']
        matches = '%s.*ro,context=\\"system_u:object_r:svirt_sandbox_file_t.*\\",nosuid,nodev.*' % mount_option
    if option == "--live":
        result = mkfile[0]['dest']
        expected_output = target_file
        matches = '%s.*rw,context=\\"system_u:object_r:svirt_sandbox_file_t.*\\",relatime,nouuid.*' % mount_option
    if option == "--shared":
        result = mkfile[0]['msg']
        matches = '%s.*ro,context=system_u:object_r:usr_t:s0,nosuid,nodev,relatime,nouuid.*' % mount_option

    assert expected_output in result, "Error cannot find '%s' in '%s'" % (matches, result)

    assert context.remote_cmd('shell',
                              module_args='grep -E "%s" /proc/mounts' % matches)

@when(u'switch atomic host to "{mode}" mode')
@when(u'switch atomic host to development mode')
def step_impl(context, mode="development"):
    '''Prepare the current deployment for hotfix or development mode'''
    opt_dict = {"development": "", "hotfix": "--hotfix"}
    assert context.remote_cmd(cmd='command',
                              module_args='atomic host unlock %s' % opt_dict[mode])

@then(u'check unlock status "{mode_str}" exists')
@then(u'check unlock status "{mode_str}" does not exists "{ignore_rc}"')
def step_impl(context, mode_str, ignore_rc='false'):
    '''Check unlock status'''
    rc = string_to_bool(context, ignore_rc)
    ostree_status = get_ostree_admin_status(context)
    if rc:
        assert mode_str not in ostree_status, "Can still find '%s' in %s" % (mode_str, ostree_status)
    else:
        assert mode_str in ostree_status, "Can't find '%s' in %s" % (mode_str, ostree_status)

@when(u'create file "{target_file}"')
def step_impl(context, target_file="/usr/unlock_test"):
    ''''''
    mkfile = context.remote_cmd('file',
                                module_args='path=%s state=touch' % target_file)
    assert mkfile, "Failed to create %s" % target_file

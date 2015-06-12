'''test methods related to Red Hat Enterprise Linux, e.g. entitlement'''

from behave import *
import ConfigParser
import re
from distutils.version import LooseVersion

config = ConfigParser.ConfigParser()
config.read('config/uat.cfg')
rh_gpg_fingerprint = '567E 347A D004 4ADE 55BA  8A5F 199E 2F91 FD43 1D51'
rh_gpg_fingerprint_short = '199E2F91FD431D51'

@when(u'"{host}" host is auto-subscribed to "{env}"')
@when(u'"{host}" is auto-subscribed')
def step_impl(context, host, env="prod"):
    '''Subscribe remote machine'''

    env_section = "redhat-%s" % env
    user = config.get(env_section, 'user')
    passwd = config.get(env_section, 'pass')
    hostname = config.get(env_section, 'hostname')
    baseurl = config.get(env_section, 'baseurl')

    if hostname:
        # we are registering against non-prod, update rhsm.conf
        assert context.remote_cmd("ini_file",
               host,
               module_args="dest=/etc/rhsm/rhsm.conf section=server option=hostname value=%s backup=yes" % hostname)
    if baseurl:
        # we are registering against non-prod, update rhsm.conf
        assert context.remote_cmd("ini_file",
               host,
               module_args="dest=/etc/rhsm/rhsm.conf section=rhsm option=baseurl value=%s backup=yes" % baseurl)

    assert context.remote_cmd("command",
           host,
           module_args="subscription-manager register --username %s --password %s --auto-attach" % (user, passwd))

@then('"{host}" host is unsubscribed and unregistered')
def step_impl(context, host):
    '''Unregister remote host'''

    r = context.remote_cmd("command",
                           host,
                           module_args="subscription-manager unregister")
    assert r

@then(u'subscription status is ok on "{host}"')
def step_impl(context, host):
    r = context.remote_cmd("command",
                           host,
                           module_args="subscription-manager status")
    assert r

    for i in r:
        assert 'Status: Current' in i['stdout']

@then(u'"{total}" entitlement is consumed on "{host}"')
def step_impl(context, total, host):
    '''Verify consumed entitlements'''
    r = context.remote_cmd("command",
                           host,
                           module_args='subscription-manager list --consumed')
    assert r

    for i in r:
        assert int(total) == i['stdout'].count('Serial')

@then(u'subscription status is unknown on "{host}"')
def step_impl(context, host):
    r = context.remote_cmd("command",
                           host,
                           ignore_rc=True,
                           module_args="subscription-manager status")
    assert r
    
    for i in r:
        assert 'Status: Unknown' in i['stdout']

@given(u'cloud-init on "{host}" host is running')
def step_imp(context,host):
	cloudinit_is_active = context.remote_cmd(cmd='command',
					host=host,
					module_args='systemctl is-active cloud-init')
	assert cloudinit_is_active, "The cloud-init service is not running"

@then(u'wait for rh_subscription_manager plugin to finish')
def step_impl(context):
	cloudinit_completed = context.remote_cmd(cmd='wait_for',
					module_args = 'path=/var/log/cloud-init.log search_regex=complete')

	assert cloudinit_completed[0].has_key('failed') == False, "The cloud-init service did not complete"

@then(u'check if the rh_subscription_manager completed successfully')
def step_impl(context):
	cloudinit_result = context.remote_cmd(cmd='shell',
					module_args='grep cc_rh_subscription.py /var/log/cloud-init.log | tail -n1 | cut -d ":" -f4 | sed "s/^ //"')[0]['stdout']
	assert cloudinit_result == 'rh_subscription plugin completed successfully', 'rh_subscription plugin failed'

@then(u'check if the subscription-manager successfully registered')
def step_impl(context):
	register_result =  context.remote_cmd(cmd='shell',
                    module_args='grep cc_rh_subscription.py /var/log/cloud-init.log | grep Regist | cut -d ":" -f4 | sed -e "s/^ //" -e "s/ [-a-f0-9]\+//" -e "s/ $//"')[0]['stdout']
	assert register_result == 'Registered successfully with ID', "subscription-manager did not register successfully"

@then(u'check if subscription-manager successfully attached existing pools')
def step_impl(context):
	pools_attached = context.remote_cmd(cmd='shell',
					module_args='grep cc_rh_subscription.py /var/log/cloud-init.log | grep pools | cut -d ":" -f5 | sed "s/^ //"')[0]['stdout']
	assert pools_attached == '8a85f9823e3d5e43013e3ddd4e9509c4', "Configured pools weren't attached"

@then(u'check if the existing listed repoids were enabled')
def step_impl(context):
	repoids_enabled = context.remote_cmd(cmd='shell',
                    module_args='grep cc_rh_subscription.py /var/log/cloud-init.log | grep "Enabled the following repos" | cut -d ":" -f5 | sed "s/^ //"')[0]['stdout']
	assert repoids_enabled == 'rhel-7-server-optional-beta-rpms, rhel-7-server-beta-debug-rpms', "Configured repoids weren't enabled"

@then(u'check if the rh_subscription_manager failed to complete')
def step_impl(context):
	cloudinit_result = context.remote_cmd(cmd='shell',
					module_args='grep cc_rh_subscription.py /var/log/cloud-init.log | tail -n1 | cut -d ":" -f4 | sed "s/^ //"')[0]['stdout']
	assert cloudinit_result == 'rh_subscription plugin did not complete successfully', 'rh_subscription plugin should have failed'

@then(u'check if the subscription-manager failed to register with bad username')
def step_impl(context):
	register_result =  context.remote_cmd(cmd='shell',
                    module_args='grep cc_rh_subscription.py /var/log/cloud-init.log | grep Invalid | cut -d ":" -f4 | sed -e "s/^ //" | tail -n1')[0]['stdout']
	assert register_result == 'Invalid username or password. To create a login, please visit https', "subscription-manager didn't fail to register"

@then(u'check if the subscription-manager failed to register with bad password')
def step_impl(context):
	register_result =  context.remote_cmd(cmd='shell',
                    module_args='grep cc_rh_subscription.py /var/log/cloud-init.log | grep Invalid | cut -d ":" -f4 | sed -e "s/^ //" | tail -n1')[0]['stdout']
	assert register_result == 'Invalid username or password. To create a login, please visit https', "subscription-manager didn't fail to register"

@then(u'check if the subscription-manager failed to attach non-existent pool-id')
def step_impl(context):
	register_result =  context.remote_cmd(cmd='shell',
                    module_args='grep cc_rh_subscription.py /var/log/cloud-init.log | grep Pool | cut -d ":" -f4 | sed -e "s/^ //"')[0]['stdout']
	assert register_result == 'Pool 8a85f9823e3d5e43013e3ddd4e95ffff is not available', "Pool 8a85f9823e3d5e43013e3ddd4e95ffff shouldn't be available"

@then(u'check if the subscription-manager failed to attach pool-id defined as a scalar')
def step_impl(context):
	register_result =  context.remote_cmd(cmd='shell',
                    module_args='grep cc_rh_subscription.py /var/log/cloud-init.log | grep Pool | cut -d ":" -f4 | sed -e "s/^ //"')[0]['stdout']
	assert register_result == 'Pools must in the format of a list.', "Pools in scalar form shouldn't be accepted"

@then(u'check if an error message is shown in the log when trying to add non-existent repo')
def step_impl(context):
	register_result =  context.remote_cmd(cmd='shell',
                    module_args='grep cc_rh_subscription.py /var/log/cloud-init.log | grep Repo | grep exist | cut -d ":" -f4 | sed -e "s/^ //"')[0]['stdout']
	assert register_result == 'Repo rhel-7-server-beta-debug-rpm does not appear to exist', "Error message not found"

@then(u'check the Repo "{reponame}" is already enabled message appearance')
def step_impl(context, reponame):
	register_result =  context.remote_cmd(cmd='shell',
                    module_args='grep cc_rh_subscription.py /var/log/cloud-init.log | grep Repo | grep already | cut -d ":" -f4 | sed -e "s/^ //"')[0]['stdout']
	repo_message = 'Repo ' + reponame + ' is already enabled'
	assert register_result == repo_message, "Informational error message not found"

@then(u'check the Repo "{reponame}" not disabled because it is not enabled message appearance')
def step_impl(context, reponame):
	register_result =  context.remote_cmd(cmd='shell',
                    module_args='grep cc_rh_subscription.py /var/log/cloud-init.log | grep Repo | grep disabled | cut -d ":" -f4 | sed -e "s/^ //"')[0]['stdout']
	repo_message = 'Repo ' + reponame + ' not disabled because it is not enabled'
	assert register_result == repo_message, "Informational error message not found"

@then(u'check if the subscription-manager issued error message when incorrect subscription keys are provided')
def step_impl(context):
	register_result =  context.remote_cmd(cmd='shell',
                    module_args='grep cc_rh_subscription.py /var/log/cloud-init.log | grep "not a valid key" | cut -d ":" -f4 | sed -e "s/^ //"')[0]['stdout']
	assert register_result == 'list is not a valid key for rh_subscription. Valid keys are', "Error message not found"

@when(u"import Red Hat's release key 2 to the superuser's keyring succeeds")
def step_impl(context):
    assert context.remote_cmd("command",
           module_args="gpg --import /etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release"), "import of Red Hat's release key 2 failed"

@then(u"verify if Red Hat's release key 2 matches public fingerprint")
def step_impl(context):
	gpg_out = context.remote_cmd("command", module_args="gpg --fingerprint")[0]['stdout']
	m = re.search(rh_gpg_fingerprint, gpg_out)
	assert m.group(0) == rh_gpg_fingerprint, "the imported Red Hat's release key 2 does not match its public fingerprint"

@when(u'download "{file}" script with sha256sum "{sha256sum}" finishes')
def step_impl(context, file, sha256sum):
	download_status = context.remote_cmd("get_url", module_args="url=" + file + " dest=/tmp/gpgverify.py force=yes sha256sum=" + sha256sum)
	assert download_status[0].has_key('failed') == False, "the gpgverify.py either failed to download or its checksum was invalid"

@when(u'OSTree version is lower than "{version}"')
def step_impl(context, version):
	atomic_host_status =  context.remote_cmd(cmd='shell',
                    module_args='atomic host status | grep "^*"')[0]['stdout']
	running_version = " ".join(atomic_host_status.split()).split()[3]
	if not LooseVersion(running_version) < LooseVersion(version): 
		context.scenario.skip(reason='OSTree version is greater or equal than ' + version + '. Skipping this scenario')

@then(u'use the gpgverify.py script to verify gpg signatures')
def step_impl(context):
	atomic_host_status =  context.remote_cmd(cmd='shell',
                    module_args='atomic host status | grep "^*"')[0]['stdout']
	treeid = " ".join(atomic_host_status.split()).split()[4]
	chmod_status =  context.remote_cmd(cmd='file',
                    module_args='path=/tmp/gpgverify.py mode=0755')
	assert chmod_status[0].has_key('failed') == False, "attempt to chmod 0755 /tmp/gpgverify.py failed"
	gpgverify_out =  context.remote_cmd(cmd='command',
                    module_args='/tmp/gpgverify.py /sysroot/ostree/repo ' + treeid)
	assert gpgverify_out, "the gpgverify.py script crashed, the OSTree isn't signed"
	m = re.search('(?<==> )(\w+)',gpgverify_out[0]['stdout'])
	commit_path = '/sysroot/ostree/repo/objects/' + m.group(0)[:2] + '/' + m.group(0)[2:] + '.commit'
	gpg_out =  context.remote_cmd(cmd='command',
                    module_args='gpg --verify sig.0 ' + commit_path)
	assert gpg_out, "verification of the gpg signature has failed"
	m = re.search('(?<=Primary key fingerprint: )(.*)',gpg_out[0]['stderr'])
	primary_key = m.group(0)
	assert primary_key == rh_gpg_fingerprint, "the OSTree signature does not match Red Hat's release key 2"

@then(u'use ostree show command to verify gpg signatures')
def step_impl(context):
	atomic_host_status =  context.remote_cmd(cmd='shell',
                    module_args='atomic host status | grep "^*"')[0]['stdout']
	tree_version = " ".join(atomic_host_status.split()).split()[3]
	treeid = " ".join(atomic_host_status.split()).split()[4]
	signature_status =  context.remote_cmd(cmd='shell',
                    module_args='ostree show ' + treeid + ' | grep ' + rh_gpg_fingerprint_short)
	assert signature_status, "OSTree version " + tree_version + " isn't signed by Red Hat's release key 2"

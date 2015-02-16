'''test methods related to Red Hat Enterprise Linux, e.g. entitlement'''

from behave import *
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('config/uat.cfg')

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
    for i in r:
        assert 'Status: Current' in i['stdout']

@then(u'"{total}" entitlement is consumed on "{host}"')
def step_impl(context, total, host):
    '''Verify consumed entitlements'''
    r = context.remote_cmd("command",
                           host,
                           module_args='subscription-manager list --consumed')
    for i in r:
        assert int(total) == i['stdout'].count('Serial')

@then(u'subscription status is unknown on "{host}"')
def step_impl(context, host):
    r = context.remote_cmd("command",
                           host,
                           module_args="subscription-manager status")
    for i in r:
        assert 'Status: Unknown' in i['stdout']
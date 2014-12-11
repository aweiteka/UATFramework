'''test methods related to Red Hat Enterprise Linux, e.g. entitlement'''

from behave import *
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('uat.cfg')

@then(u'"{host}" host is auto-subscribed')
def step_impl(context, host):
    '''Subscribe remote machine'''

    user = config.get('redhat', 'user')
    passwd = config.get('redhat', 'pass')
    r = context.remote_cmd(host,
                           "subscription-manager",
                           module_args="register --username %s --password %s --auto-attach") % (user, passwd)
    assert False

@given(u'subscription status is ok on "{host}"')
def step_impl(context):
    r = context.remote_cmd(host,
                           "subscription-manager",
                           module_args="status")
    assert False

@then(u'"{total}" entitlement is consumed on "{host}"')
def step_impl(context, total, host):
    '''Verify consumed entitlements'''
    r = context.remote_cmd(host,
                           "command",
                           module_args='subscription-manager list --consumed')
    assert int(total) == r['stdout'].count('Serial')


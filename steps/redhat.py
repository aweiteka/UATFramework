'''test methods related to Red Hat Enterprise Linux, e.g. entitlement'''

from behave import *
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('config/uat.cfg')

@when(u'"{host}" host is auto-subscribed')
def step_impl(context, host):
    '''Subscribe remote machine'''

    user = config.get('redhat', 'user')
    passwd = config.get('redhat', 'pass')
    r = context.remote_cmd("command",
                           host,
                           module_args="subscription-manager register --username %s --password %s --auto-attach" % (user, passwd))
    assert r

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

@then(u'"{total}" entitlement is consumed on "{host}"')
def step_impl(context, total, host):
    '''Verify consumed entitlements'''
    r = context.remote_cmd("command",
                           host,
                           module_args='subscription-manager list --consumed')
    for i in r:
        assert int(total) == i['stdout'].count('Serial')


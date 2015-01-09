'''test methods related to vagrant'''

from behave import *
#import ConfigParser

#config = ConfigParser.ConfigParser()
#config.read('config/uat.cfg')

#@then(u'subscription status is ok on "{host}"')
#def step_impl(context):
#    r = context.remote_cmd(host,
#                           "subscription-manager",
#                           module_args="status")
#    assert False

@given(u'vagrant plugin "{plugin}" is installed')
def step_impl(context, plugin, host="cihosts"):
    assert context.remote_cmd("command",
                              host,
                              module_args="vagrant plugin install %s" % plugin)

@given(u'vagrant plugin "{plugin}" is verified')
def step_impl(context, plugin, host="cihosts"):
    r = context.remote_cmd("command",
                           host,
                           module_args="vagrant plugin list")
    assert r.index(plugin) >= 0

@given(u'vagrant box "{box}" is already installed')
def step_impl(context, box, host="cihosts"):
    r = context.remote_cmd("command",
                           host,
                           module_args="vagrant box list")
    assert r.index(box) >= 0

@given(u'Clone CDK from "{url}"')
def step_impl(context, url, host="cihosts"):
    assert context.remote_cmd("git",
                              host,
                              module_args="repo=%s dest=~/cdk" % url)

@when(u'Vagrantfile is linked')
def step_impl(context, host="cihosts"):
    assert context.remote_cmd("file",
                              host,
                              module_args="src=~/cdk/components/standalone-rhel/Vagrantfile dest=~/Vagrantfile state=link")

@when(u'vagrant up')
def step_impl(context, host="cihosts"):
    assert context.remote_cmd("command",
                              host,
                              module_args="vagrant up")

@then(u'vagrant connect to "{guest}"')
def step_impl(context, guest, host="cihosts"):
    assert context.remote_cmd("command",
                              host,
                              module_args="vagrant up")


@then(u'vagrant "{guest}" is destroyed')
def step_impl(context, guest, host="cihosts"):
    assert context.remote_cmd("command",
                              host,
                              module_args="vagrant up")

@then(u'vagrant "{guest}" is auto-subscribed')
def step_impl(context, guest, host="cihosts"):
    assert False

@then(u'vagrant "{guest}" is unsubscribed and unregistered')
def step_impl(context, guest, host="cihosts"):
    assert False


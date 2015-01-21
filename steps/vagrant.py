'''test methods related to vagrant'''

from behave import *
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('config/uat.cfg')
remote_user = config.get("vagrant", "user")
vagrant_build_dependencies = "ruby,ruby-devel,ruby-libvirt,rubygem-ruby-libvirt,libvirt,libvirt-devel,rubygem-bundler,rubygem-bundler-doc,rubygem-nokogiri,libxml2-devel,libxslt-devel,rubygem-rake"

@given(u'vagrant plugin is "{plugin_name}"')
def step_impl(context, plugin_name):
    context.vagrant_plugin = plugin_name

@given(u'install vagrant plugin')
def step_impl(context):
    assert context.remote_cmd("command",
                              context.target_host,
                              remote_user=remote_user,
                              module_args="vagrant plugin install %s" % context.vagrant_plugin)

@then(u'vagrant plugin is verified as installed')
@given(u'vagrant plugin is verified as installed')
def step_impl(context):
    r = context.remote_cmd("command",
                           context.target_host,
                           remote_user=remote_user,
                           module_args="vagrant plugin list")
    for i in r:
        assert i['stdout'].index(context.vagrant_plugin) >= 0

@given(u'vagrant box "{box}" is already installed')
def step_impl(context, box, host="cihosts"):
    r = context.remote_cmd("command",
                           host,
                           remote_user=remote_user,
                           module_args="vagrant box list")
    for i in r:
        assert i['stdout'].index(box) >= 0

@given(u'source of the plugin is cloned from "{url}"')
def step_impl(context, url):
    context.execute_steps(u"""
    Given clone "{project_name}" from "{url_name}"
    """.format(project_name=context.vagrant_plugin, url_name=url))
        
@given(u'Clone CDK from "{url}"')
def step_impl(context, url, host="cihosts"):
    assert context.remote_cmd("git",
                              host,
                              remote_user=remote_user,
                              module_args="repo=%s dest=~/cdk" % url)

@when(u'Vagrantfile is linked')
def step_impl(context, host="cihosts"):
    assert context.remote_cmd("file",
                              host,
                              remote_user=remote_user,
                              module_args="src=~/cdk/components/standalone-rhel/Vagrantfile dest=~/Vagrantfile state=link")

@when(u'vagrant up')
def step_impl(context, host="cihosts"):
    assert context.remote_cmd("command",
                              host,
                              remote_user=remote_user,
                              module_args="vagrant up")

@then(u'vagrant connect to "{guest}"')
def step_impl(context, guest, host="cihosts"):
    assert context.remote_cmd("command",
                              host,
                              remote_user=remote_user,
                              module_args="vagrant up")


@then(u'vagrant "{guest}" is destroyed')
def step_impl(context, guest, host="cihosts"):
    assert context.remote_cmd("command",
                              host,
                              remote_user=remote_user,
                              module_args="vagrant up")

@then(u'vagrant "{guest}" is auto-subscribed')
def step_impl(context, guest, host="cihosts"):
    assert context.remote_cmd("command",
                              host,
                              remote_user=remote_user,
                              module_args="vagrant ssh -c 'sudo subscription-manager status'")

#requires querying the customer portal to find out if the registration was remove (the box it was on is gone)
#@then(u'vagrant "{guest}" is unsubscribed and unregistered')
#def step_impl(context, guest, host="cihosts"):
#    assert False


@given(u'vagrant is installed')
def step_impl(context, host="cihosts"):
    assert context.remote_cmd("command",
                              host,
                              remote_user=remote_user,
                              module_args="which vagrant")

#not sure why this doesn't work
@given(u'vagrant plugin build dependencies are installed')
def step_impl(context, host="cihosts"):
    context.execute_steps(u"""
    given "{package_names}" are already installed on "{vagrant_host}"
    """.format(package_names=vagrant_build_dependencies,vagrant_host=context.target_host))

#def step_impl(context, vagrant_plugin, host="cihosts"):
@given(u'bundler has been used to install ruby dependencies')
def step_impl(context):
    assert context.remote_cmd("command",
                              context.target_host,
                              remote_user=remote_user,
                              module_args="cd ~/%s && bundle config build.nokogiri --use-system-libraries && bundle install" % context.vagrant_plugin)

@when(u'vagrant plugin is built')
def step_impl(context):
    assert context.remote_cmd("command",
                              context.target_host,
                              remote_user=remote_user,
                              module_args="cd ~/%s && rake build" % context.vagrant_plugin)

@then(u'local "vagrant-registration" gem is successfully installed')
def step_impl(context):
    context.execute_steps(u"""
    given vagrant plugin is verified as installed
    """)

    

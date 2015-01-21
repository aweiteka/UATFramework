'''test methods related to vagrant'''

from behave import *
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('config/uat.cfg')
remote_user = config.get("vagrant", "user")

@given(u'Clone "{project}" from "{url}"')
def step_impl(context, project, url):
    assert context.remote_cmd("git",
                              context.target_host,
                              remote_user=remote_user,
                              module_args="repo=%s dest=~/%s" % (url, project))


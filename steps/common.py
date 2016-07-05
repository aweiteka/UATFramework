'''Common test methods'''

import os
import re

from behave import *


def exec_service_cmd(context, action, service_name, host=None):
    if host == None:
        host = context.target_host

    #cmd = context.service_cmd
    cmd = "systemctl ACTION SERVICE_NAME"
    cmd = re.sub("ACTION", action, cmd)
    cmd = re.sub("SERVICE_NAME", service_name, cmd)

    result = context.remote_cmd(cmd='command',
                                host=host,
                                module_args=cmd,
                                ignore_rc=True)

    if action == "status":
        emsg = "Can not get the status of service %s" % service_name
    else:
        emsg = "Can not %s service %s" % (action, service_name)

    assert result, emsg

    return result[0]['stdout']

def string_to_bool(context, string):
    '''convert string to bool'''
    bool_dict = {'false':False, 'False': False, 'true':True, 'True': True}
    return bool_dict[string]

@given(u'get the services from configure file')
def step_impl(context):
    svcs_all = {}
    for item in context.test_cfg.items('service_check'):
        svcs_all[item[0]] = item[1].split()
    context.svcs_all = svcs_all


@then(u'update services original status')
def step_impl(context):
    status_data = {}
    svcs_disabled = {}
    svcs_running = {}
    svcs_not_exist = {}
    load_pattern = "Loaded:.*(disable|enable)"
    active_pattern = "Active:.*(running)"

    for host in context.svcs_all:
        svcs_disabled[host] = []
        svcs_running[host] = []
        for svc in context.svcs_all[host]:
            status = exec_service_cmd(context, 'status', svc, host)

            loaded = re.findall(load_pattern, status)
            if not loaded:
                if host not in svcs_not_exist:
                    svcs_not_exist[host] = []
                svcs_not_exist[host].append(svc)
                context.svcs_all[host].remove(svc)
                continue
            if loaded == "disabled":
                svcs_disabled[host].append(svc)

            running = re.findall(active_pattern, status)
            if running:
                svcs_running[host].append(svc)

    context.svcs_running = svcs_running
    context.svcs_disabled = svcs_disabled

    emsg = ""
    for host in svcs_not_exist:
        emsg += "For host %s, service " % host
        emsg += "'%s' is not exist" % " ".join(svcs_not_exist[host])
    assert not svcs_not_exist, emsg


@then(u'setup services based on configure file')
def step_impl(context):
    """Set up services status based on the options in cfg files.
       The actions is set as prefix in options, and host is set
       as suffix. If no host is specific, the action will be applied
       in all hosts.
    """
    hosts = context.get_hosts().keys()
    hosts.remove("ungrouped")
    hosts.remove("all")
    hosts.insert(0, "all")
    for action in ["enable", "disable", "restart", "stop"]:
        for host in hosts:
            services = []
            option_name = "%s_services" % action
            if hasattr(context, option_name):
                services = getattr(context, option_name).split()
            option_name = "%s_services_%s" % (action, host)
            if hasattr(context, option_name):
                services = getattr(context, option_name).split()
            for service in services:
                exec_service_cmd(context, action, service, host)


@given(u'"{action}" "{status}" services')
@then(u'"{action}" "{status}" services')
def step_impl(context, action, status):
    svcs = getattr(context, "svcs_%s" % status, None)
    assert svcs, "Can not find %s service from context" % status

    for host in svcs:
        for svc in svcs[host]:
            exec_service_cmd(context, action, svc, host)


@when(u'services status is "{status}"')
@then(u'services status is "{status}"')
def step_impl(context, status):
    if status in ['running', 'dead', 'active', 'inactive', 'start']:
        pattern = r"Active:.*?(%s)" % status
        msg_pattern = r"Active:.*"
    else:
        pattern = r"Loaded:.*?(%s)" % status
        msg_pattern = r"Loaded:.*"

    svcs = context.svcs_all

    emsg = ""
    for host in svcs:
        for svc in svcs[host]:
            current_status = exec_service_cmd(context, "status", svc, host)
            if not re.findall(pattern, current_status):
                msg = re.findall(msg_pattern, current_status)[0]
                emsg += ("Service %s in host %s is not %s but '%s'" %
                         (svc, host, status, msg))

    assert emsg == "", emsg


@given(u'"{host}" hosts from dynamic inventory')
def step_impl(context, host):
    context.inventory = "dynamic"
    context.target_host = host

@given(u'"{host}" hosts from static inventory')
def step_impl(context, host):
    context.inventory = "static"
    context.target_host = host

@given(u'"{rpm}" is already installed on "{host}"')
def step_impl(context, rpm, host):
    '''Install RPM on host but fail if not already installed'''
    r = context.remote_cmd("yum",
                           host,
                           remote_user="root",
                           module_args='name=%s state=present' % rpm)
    if r:
        for i in r:
            assert i['msg'] == '' and i['results'] != []
    else:
        assert False

@given(u'"{rpm}" is already installed')
def step_impl(context, rpm):
    '''Install RPM on host but fail if not already installed'''
    context.execute_steps(u"""
    given "{package_name}" is already installed on "{host}"
    """.format(package_name=rpm, host=context.target_host))

@given(u'"{rpms}" are already installed on "{host}"')
def step_impl(context, rpms, host):
    '''Install RPM on host but fail if not already installed'''
    r = context.remote_cmd("yum",
                           host,
                           remote_user="root",
                           module_args='name=%s' % rpms)
    if r:
        for i in r:
            assert i['msg'] == '' and i['results'] != []
    else:
        assert False

@given(u'"{rpms}" are already installed')
def step_impl(context, rpms):
    '''Install RPM on host but fail if not already installed'''
    context.execute_steps(u"""
    "given {package_names}" are already installed on "{host}"
    """.format(package_names=rpms, host=context.target_host))

@given(u'"{unit}" is already running on "{host}"')
def step_impl(context, unit, host):
    '''Ensure service is running but fail if not'''
    r = context.remote_cmd("service",
                           host,
                           module_args='name=%s state=running enabled=yes' % unit)
    if r:
        for i in r:
            assert i['changed'] is False
    else:
        assert False

@then(u'"{unit}" is started and enabled on "{host}"')
def step_impl(context, unit, host):
    '''Start service but fail if already running'''
    r = context.remote_cmd('service',
                           host,
                           module_args='name=%s state=running enabled=yes' % unit)
    if r:
        for i in r:
            assert i['state'] == 'started' and i['enabled'] is True
    else:
        assert False

@then(u'"{unit}" is restarted on "{host}"')
def step_impl(context, unit, host):
    '''Restart service'''
    r = context.remote_cmd('service',
                           host,
                           module_args='name=%s state=restarted' % unit)
    if r:
        for i in r:
            assert i['state'] == 'started' and i['changed'] is True
    else:
        assert False

@given(u'"{host}" hosts can be pinged')
@given('"{host}" host')
def step(context, host):
    '''Verify we can ping the host

    host: a host from the ansible inventory file'''
    assert context.remote_cmd('ping', host)

@then('run command "{cmd}"')
@given('run command "{cmd}" on "{host}"')
@when('run command "{cmd}" on "{host}"')
@then('run command "{cmd}" on "{host}"')
@then('run command "{cmd}" ignore error "{ignore_rc}"')
def step(context, cmd, host=None, ignore_rc='false'):
    '''Run an Ansible module on a host directly from scenario

    cmd: a module name plus arguments
         <module> key=value [key=value ...]
         or...
         <module> <param>
    host: a host from the inventory file'''
    ignore_rc = string_to_bool(context, ignore_rc)
    module, args = None, None
    if ' ' in cmd:
        # we only split on the first space to get the module name
        # since module_args are also space-delimited
        module, args = cmd.split(' ', 1)
    else:
        module = cmd
    assert context.remote_cmd(module,
                              host,
                              ignore_rc=ignore_rc,
                              module_args=args)

@when('checkout the git repo "{repo}" on "{host}"')
@given('checkout the git repo "{repo}" on "{host}"')
def step(context, repo, host):
    "Checkout a git repo on remote host"
    r = context.remote_cmd('git',
                            host,
                            module_args='repo=%s dest=/root/tools' % repo)
    assert r, "The checkout of the git repo " + repo + " didn't complete successfully"

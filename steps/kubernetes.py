'''test methods for kubernetes'''

import re
import json
import time
from jinja2 import Environment, FileSystemLoader
from behave import *

# Jinja2 requires an Environment to be set up in order to load templates from
# the file system (see http://jinja.pocoo.org/docs/dev/api/#basics).
j2env = Environment(loader=FileSystemLoader('steps/kube_resources'))


def kubectl_get(context, component):

    # NB: Note that we aggregate across masters. This doesn't matter in reality
    # since our cluster test uses only one master. But if we ever change to
    # using multiple masters, things will be different.

    r = context.remote_cmd('command',
                           module_args='kubectl get %s -o json' % component)
    assert r, "unable to get %s" % component

    items = []
    for i in r:
        data = json.loads(i['stdout'])
        if 'items' in data:
            items.extend(data['items'])
    return items


def kubectl_create(context, resource):
    r = context.remote_cmd('command',
                           module_args='kubectl create -f %s' % resource)
    assert r, "could not create resource %s" % resource


def kubectl_exec(context, pod_name, command):
    # NB: do not be confused by the r[i]['rc'] value. The `kubectl exec`
    # command will always return 0 even if the exec'ed command returns a
    # non-zero. If r[i]['rc'] is nonzero, then it means that something went
    # wrong with kubernetes itself (e.g. pod doesn't exist).
    r = context.remote_cmd('command',
                           module_args='kubectl exec %s -- %s' % (pod_name,
                                                                  command))
    assert r, "failed to kubectl exec %s" % command
    return r


def send_kube_resource(context, resource):
    resource = 'steps/kube_resources/%s' % resource
    r = context.remote_cmd('copy', module_args='src=%s dest=.' % resource)
    assert r, "unable to send %s" % resource


def render_template(filename, **kwargs):
    template = j2env.get_template(filename + '.j2')
    rendered = template.render(**kwargs)
    with open('steps/kube_resources/' + filename, 'wb') as f:
        f.write(rendered)


def render_template_and_send(context, filename, **kwargs):
    render_template(filename, **kwargs)
    send_kube_resource(context, filename)


def node_is_ready(node):
    for condition in node['status']['conditions']:
        if condition['type'] == "Ready":
            return condition['status'] == 'True'
    return False


def find_pod(context, pod_name):
    for pod in kubectl_get(context, "pods"):
        if pod["metadata"]["name"] == pod_name:
            return pod


def pod_is_running(context, pod_name):

    pod = find_pod(context, pod_name)
    assert pod

    if pod['status']['phase'] != 'Running':
        return False

    for condition in pod['status']['conditions']:
        if condition['type'] == "Ready":
            return condition['status'] == 'True'

    return False


def get_node_name_from_idx(context, node_idx):
    node = kubectl_get(context, "nodes")[node_idx]
    return node['metadata']['name']


def find_svc(context, svc_name):
    for svc in kubectl_get(context, "services"):
        if svc["metadata"]["name"] == svc_name:
            return svc


@given('"{number}" "{component}" are running')
def step_impl(context, number, component):
    '''check expected number of components are running
       where component is pod, service, node, etc'''
    assert len(kubectl_get(context, component)) is int(number)


@given('nodes are ready')
def step_impl(context):
    for node in kubectl_get(context, "nodes"):
        assert node_is_ready(node)


@when('the "{pod_name}" pod is running on node "{node_idx}"')
def step_impl(context, pod_name, node_idx):
    '''Check whether a pod exists on node. If it isn't, create it. The pod
       definition is found in the kube_resources/ dir. Its final name will be
       {pod_name}-{node_idx}.'''

    # construct the final name for this pod
    name = pod_name + '-' + node_idx

    # does this pod already exist?
    if not find_pod(context, name):

        # ok, we need to create it. let's start by rendering its definition
        # from the template and sending it over.
        filename = pod_name + '-pod.yaml'

        # NB: we do -1 here because Python is (obviously) 0-based, but when we
        # describe it in the feature, we use 1-based indexing.
        node_name = get_node_name_from_idx(context, int(node_idx)-1)
        render_template_and_send(context,
                                 filename,
                                 pod_name=name,
                                 node_name=node_name)

        # ok, now we can actually create the resource
        kubectl_create(context, filename)

        # check that the pod now exists
        assert find_pod(context, name)

        # give up to 5 minutes for it to start running (the image needs time to
        # get downloaded)
        i = 5*60
        polling_interval = 10
        while not pod_is_running(context, name) and i > 0:
            time.sleep(polling_interval)
            i -= polling_interval

    assert pod_is_running(context, name)


@then('the "{pod1_name}" pod can ping the "{pod2_name}" pod')
def step_impl(context, pod1_name, pod2_name):

    pod1 = find_pod(context, pod1_name)
    pod2 = find_pod(context, pod2_name)
    assert pod1 and pod2, "could not find pods"

    r = kubectl_exec(context, pod1_name,
                     'ping -q -c 5 %s' % pod2['status']['podIP'])
    for i in r:
        # assert ' 5 packets received, 0% packet loss' in i['stdout']

        # XXX: We cannot make the above assertion for now because of a bug in
        # flannel which causes the first ping to be lost:
        # https://github.com/coreos/flannel/issues/172
        # This bug is fixed in v0.5.0, which hasn't made it yet to the latest
        # Atomic. Once we get it, restore the stronger assertion above. For
        # now, let's assert a weaker statement:
        assert ' 100% packet loss' not in i['stdout']


@when('the "{svc_name}" service exists')
def step_impl(context, svc_name):
    '''Check whether a svc exists. If it doesn't, create it. The svc definition
       is found in the kube_resources/ dir.'''

    # does this svc already exist?
    if not find_svc(context, svc_name):

        # send over the definition and create it
        filename = svc_name + '-svc.yaml'
        send_kube_resource(context, filename)
        kubectl_create(context, filename)

    assert find_svc(context, svc_name), "the service still does not exist"


@then('the "{pod_name}" pod can resolve the "{svc_name}" service')
def step_impl(context, pod_name, svc_name):

    pod = find_pod(context, pod_name)
    assert pod, "could not find pod %s" % pod_name

    svc = find_svc(context, svc_name)
    assert svc, "could not find svc %s" % svc_name

    r = kubectl_exec(context, pod_name, 'nslookup %s' % svc_name)
    for i in r:
        assert i['stdout'].endswith(svc["spec"]["clusterIP"])


# Unfortunately, we can't make this into a generic service checker because it
# is inherently dependent on the type of service. Here for example, to check
# that httpd can be reached, we do wget httpd.
@then('the "{pod_name}" pod can reach the httpd service')
def step_impl(context, pod_name):

    pod = find_pod(context, pod_name)
    assert pod, "could not find pod %s" % pod_name

    r = kubectl_exec(context, pod_name, 'wget -qO- httpd')
    for i in r:
        assert "Hello World" in i['stdout']

'''test methods for docker'''

import re
import os
from behave import *


def get_running_container_id(context):
    '''get running container id'''
    container_result = context.remote_cmd(cmd='command',
                                        module_args='docker ps')

    assert container_result, "Error running 'docker ps'"

    container_re = re.compile(r'^(?P<container>\w{12})'
                              r'\s*(?P<image>[\w:]+)'
                              r'\s*(?P<command>[\w/]+)'
                              r'\s*(?P<created>[\w]+)'
                              r'\s*(?P<status>[\w]+)'
                              r'\s*(?P<ports>[\d]*)'
                              r'\s*(?P<names>[\w_]+)')

    container_id = None
    for item in container_result:
        for l in item['stdout'].split('\n'):
            m = container_re.search(l)
            if m:
                container_id = m.group('container')

    return container_id

def get_images_id(context):
    '''get images id'''
    images_result = context.remote_cmd(cmd='command',
                                       module_args='docker images -q')
    for image in images_result:
        return image['stdout'].split('\n')

@when('docker pull "{image}"')
def step_impl(context, image):
    '''docker pull image'''
    assert context.remote_cmd('command',
                               module_args='docker pull %s' % image)

@then(u'remove docker image "{image}"')
def step_impl(context, image):
    assert context.remote_cmd('command',
                               module_args='docker rmi -f %s' % image)

@then(u'rpm "{rpm}" is installed in "{image}" on "{host}"')
def step_impl(context, rpm, image, host):
    '''docker run and install RPM'''
    assert context.remote_cmd('command',
                               host,
                               module_args='docker run %s yum install -y %s' % (image, rpm))

@when('docker stop container')
def step_impl(context):
    '''docker stop container'''
    container_id = get_running_container_id(context)
    assert container_id, "There is not a running container"
    assert context.remote_cmd('command',
                               module_args='docker stop %s' % container_id)

@when('docker run "{image}" detach mode with "{command}"')
def step_impl(context, image, command):
    '''docker run image with detach mode'''
    assert context.remote_cmd('command',
                               module_args='docker run -d %s %s' % (image, command))

@then('check whether there is a running container')
def step_impl(context):
    '''check whether container is running'''
    container_id = get_running_container_id(context)
    assert container_id, "There is not a running container"

@when('docker build an image from local "{dockerfile}"')
@when('docker build an image from local "{path}"/"{dockerfile}"')
@when('docker build an image with tag "{tag}" from local "{dockerfile}"')
def step_impl(context, dockerfile, path="/var/home/cloud-user", tag=''):
    '''Build an image from a local Dockerfile, which path default is
       /var/home/cloud-user'''
    src_file = os.path.join("resources/docker", dockerfile)
    dest_file = os.path.join(path, src_file)
    # create directory on target host
    assert context.remote_cmd('file',
                               module_args='path=%s state=directory' % os.path.dirname(dest_file))
    # remotely copy dockerfile to specified directory
    context.execute_steps(u"""
                          when "{src_file}" is copied to "{dest_file}"
                          """.format(src_file=src_file, dest_file=dest_file))
    # build image from dockerfile
    module_args = 'docker build -f %s' % dest_file
    if tag:
        module_args += ' -t %s' % tag
    assert context.remote_cmd('command',
                               module_args='%s .' % module_args)

@when('docker remove all of images')
def step_impl(context):
   '''Remove all of images'''
   assert context.remote_cmd('shell',
                             module_args='docker images -a -q | xargs -r docker rmi')

@when('docker remove all of containers')
def step_impl(context):
   '''Remove all of containers'''
   assert context.remote_cmd('shell',
                             module_args='docker ps -a -q | xargs -r docker rm')

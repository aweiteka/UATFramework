'''ostree test methods'''

import re
from behave import *


def get_ostree_admin_status(context):
    '''get ostree admin status'''
    ostree_result = context.remote_cmd(cmd='command',
                                       module_args='ostree admin status')
    assert ostree_result, "Can not get status result"
    result = ostree_result[0]['stdout']
    assert result, "Can not get deployments"
    return result


@then(u'undeploy the unselected deployment')
def step_impl(context):
    ostree_status = get_ostree_admin_status(context)
    ostree_entry = re.findall(r'.*[\d\w\.]{66}', ostree_status)

    for index, item in enumerate(ostree_entry):
        if not re.match('\*', item):
            undep_index = index
            break

    undeploy_cmd = 'ostree admin undeploy %s' % undep_index
    undeploy_result = context.remote_cmd(cmd='command',
                                         module_args=undeploy_cmd)

    assert undeploy_result, "Can not undeploy the %s deployment" % undep_index


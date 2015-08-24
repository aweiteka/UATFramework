'''ostree test methods'''

import re
from behave import *


@then(u'undeploy the unselected deployment')
def step_impl(context):
    ostree_result = context.remote_cmd(cmd='command',
                                       module_args='ostree admin status')

    assert ostree_result, "Can not get ostree status"

    ostree_status = ostree_result[0]['stdout']
    ostree_entry = re.findall(r'.*[\d\w\.]{66}', ostree_status)

    for index, item in enumerate(ostree_entry):
        if not re.match('\*', item):
            undep_index = index
            break

    undeploy_cmd = 'ostree admin undeploy %s' % undep_index
    undeploy_result = context.remote_cmd(cmd='command',
                                         module_args=undeploy_cmd)

    assert undeploy_result, "Can not undeploy the %s deployment" % undep_index


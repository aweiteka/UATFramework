'''test methods for openshift'''

from behave import *

@given('an openshift service')
def step(context):
    pass

@then('list domains')
def step(context):
    assert context.api('openshiftv2', 'domains')

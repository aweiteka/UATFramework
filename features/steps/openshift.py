from behave import *
import json

@given('an openshift service')
def step(context):
    pass

@then('list domains')
def step(context):
    assert context.api('openshiftv2', 'domains')

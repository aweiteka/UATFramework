from behave import *
import json

# POST example
@when('organization "{name}" is created')
def step(context, name):
    assert context.api('satellite',
                       'organizations',
                       '{"name": "%s", "label": "%s"}' % (name, name))

# GET example
@then('there are "{total_orgs}" organizations')
def step(context, total_orgs):
    orgs = context.api('satellite', 'organizations')
    assert len(orgs) == int(total_orgs)

# DELETE example
@when('organization "{name}" is deleted')
def step(context, name):
    assert context.api('satellite', 'organizations/%s' % name, method='delete')

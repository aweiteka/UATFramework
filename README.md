## About

This is a lightweight framework to perform User Acceptance Testing (UAT) using a Behavior Driven Development (BDD) model.

## Why another framework?

In addition to unit testing and system testing we need a simple framework to perform arbitrary automation accross products. The target is "happy path" integration testing based on use cases, not comprehensive deep-dive testing.

### Goals
* enable automation accross multiple applications. Automation must be easy to write against application APIs.
* support remote host commands via SSH
* follow Behavior Driven Development (BDD) best practice to define workflows in a semi-formal language outside of implmentation. See [BDD](http://en.wikipedia.org/wiki/Behavior-driven_development)
* test results should be displayed as pass/fail based on user stories
* plug into continuous integration (CI)
* automate application integration for stage and demonstration environments. This means the result of the test should optionally be a configured system based on executed use cases.

## Design

Automation needs to be really simple to write. If you can write a user story, a bash script and understand how to use your application's API to make `GET` and `PUT` calls you should be able to use this framework.
* Consistent interface for application APIs. Example:
```
app1("api/get/call")
myvar = app2("another/api/get/call")
app3("api/post/call", {"post": "data"})
```
* Simple SSH interface for remote host control via Ansible. Example:
```
app1("remote_host", "command to run via ssh")
```

## Getting started
Framework [Behave documentaion](http://pythonhosted.org/behave/)

Ansible [API](http://docs.ansible.com/developing_api.html) and [modules](http://docs.ansible.com/modules_by_category.html)

See [product documentation](https://access.redhat.com/documentation) for application APIs

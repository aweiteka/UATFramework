## About

This is a lightweight framework to perform User Acceptance Testing (UAT) using a Behavior Driven Development (BDD) model.

## Why another framework?

In addition to unit testing and system testing we need a simple framework to perform arbitrary automation across products. The target is "happy path" integration testing based on use cases, not comprehensive deep-dive testing.

### Goals
* enable automation accross multiple applications. Automation must be easy to write against application APIs.
* support remote host commands via SSH
* follow Behavior Driven Development (BDD) best practice to define workflows in a semi-formal language outside of implmentation. See [BDD](http://en.wikipedia.org/wiki/Behavior-driven_development)
* test results should be displayed as pass/fail based on user stories
* plug into continuous integration (CI)
* automate application integration for stage and demonstration environments. This means the result of the test should optionally be a configured system based on executed use cases.
* assume only user actions are automated with this framework. Use puppet, cloud-init, heat templates and kickstarts to take care of provisioning and initial installation configuration.

## Design

Automation needs to be *really simple* to write and maintain. If you can write a user story, a bash script and make sense of API documentation to make `GET` and `PUT` calls you should be able to use this framework.
* Consistent, simple interface for application APIs.
* Simple method for running commands on remote hosts.

## Getting started

1. Familiarize yourself with [Behave documentation](http://pythonhosted.org/behave/)
1. Understand how the examples work in this repo.
1. Make a copy of the configuration file and customize: `cp uat.template uat.cfg`
1. Create an `ansible_inventory` file for any hosts remote commands are run on: `cp ansible_inventory.template ansible_inventory`
1. Install python dependencies: `[sudo] pip install -r requirements.txt`
1. Execute tests (assumes current working directory is base of this repo)
  * Run them all: `behave`
  * Run a specific feature file: `behave features/myfile.feature`
  * Run specific scenario(s) by keyword: `behave -n <keyword>`
  * Run by tag keyword: `behave -t <tag>`
  * add `--dry-run` to see output but don't execute

### Debugging
By default debug print statements are captured with all stdout and stderr also. This makes debugging difficult. Pass argument `--no-capture` when running Behave to view debug statements. For stderr pass in `--no-capture-stderr`.

## Reference

General [product documentation](https://access.redhat.com/documentation)
* [Satellite 6](https://access.redhat.com/documentation/en-US/Red_Hat_Satellite/6.0/html-single/API_Guide/index.html)
* [OpenShift 2](https://access.redhat.com/documentation/en-US/OpenShift_Enterprise/2/html-single/REST_API_Guide/index.html)

[Ansible modules](http://docs.ansible.com/modules_by_category.html)

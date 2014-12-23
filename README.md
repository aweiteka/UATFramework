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

Automation needs to be *really simple* to write and maintain. If you can write a user story, a bash script and make sense of API documentation to make `GET` and `POST` calls you should be able to use this framework.
* Consistent, simple interface for application APIs.
* Simple method for running commands on remote hosts.
* Support dynamic host discovery for CI workflows.

## Getting started

1. Familiarize yourself with [Behave documentation](http://pythonhosted.org/behave/)
1. Understand how the examples work in this repo.
1. Make a copy of the configuration file and customize: `cp uat.cfg.sample uat.cfg`
1. Create an `ansible_inventory` file for any hosts remote commands are run on: `cp ansible_inventory.sample ansible_inventory`
1. Install python dependencies using pip. You may need to install python-devel and gcc first.

        [sudo] yum install -y python-devel gcc
        [sudo] pip install -r requirements.txt

1. Execute tests (assumes current working directory is base of this repo)
  * Run them all (very unusual): `behave`
  * Run a specific feature file (common): `behave features/myfile.feature`
  * Run specific scenario(s) by keyword (great for debugging): `behave -n <scenario_keyword>`
  * add `--dry-run` to see output but don't execute

## Writing your first test

1. Always start with a feature. This is a great time to freely think like a user and the end goal. Consider pairing up with a colleague and write the feature in 30 minutes.
1. Run the feature you just wrote: `behave features/mynew.feature`
1. Copy the output into a steps file. Some of these are already covered in existing steps. Keep them organized by target application.
1. Delete redundant steps and re-word your feature lines as necessary. If a step is not implemented, fail it with `assert False` until it's implemented.
1. Build up the steps files to support the feature. Get it green.
1. Check in the feature and get into a CI job right away. Watch it fail, fix, rinse, repeat.

### Debugging
By default debug print statements are captured with all stdout and stderr also. This makes debugging difficult. Pass argument `--no-capture` when running Behave to view debug statements. For stderr pass in `--no-capture-stderr`.

Remote commands are executed via Ansible and SSH. For new commands try using ansible CLI then add them to a steps method.

Static inventory:

    $ ansible <host_group_from_inventory> -i ansible_inventory -m command -a <some shell command>

Dynamic inventory script. Example parses 'resources.json' for a specific CI system:

    $ ansible cihosts -i central_ci_dynamic_hosts.py -m command -a <some shell command>

## Running as docker container

This is a work in progress.

1. You may need to turn off selinux so docker can read the bindmounted files on the host.

        [sudo] setenforce 0

1. There are a bunch of dependencies to mount. SSH keys are problematic.

        [sudo] docker run -it \
               -v /path/to/.ssh:/.ssh \
               -v /path/to/UATFramework/resources.json:/uatframework/resources.json \
               -v /path/to/UATFramework/uat.cfg:/uatframework/uat.cfg \
               -v /path/to/UATFramework/ansible_inventory:/uatframework/ansible_inventory \
               aweiteka/uatframework:wip [features/my.feature]

## Reference

General [product documentation](https://access.redhat.com/documentation)
* [Satellite 6](https://access.redhat.com/documentation/en-US/Red_Hat_Satellite/6.0/html-single/API_Guide/index.html)
* [OpenShift 2](https://access.redhat.com/documentation/en-US/OpenShift_Enterprise/2/html-single/REST_API_Guide/index.html)

[Ansible modules](http://docs.ansible.com/modules_by_category.html)

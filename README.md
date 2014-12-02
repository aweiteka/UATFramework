# Proof of Concept

A lightweight Behavior Driven Development (BDD) test framework to perform user acceptance testing (UAT) based on Python BDD Behave.

## Goals
* enable automation accross multiple applications. Automation must be easy to write against application APIs.
* support remote host commands via SSH
* follow BDD best practice to define workflows in a semi-formal language outside of application API. See [BDD](http://en.wikipedia.org/wiki/Behavior-driven_development)
* enable clear reporting accross applications under test for transparent results
* plug into continuous integration (CI)
* automate application integration for stage and demonstration environments

## Design
* Consistent interface for application APIs
* Simple SSH interface for remote host control via Ansible.

## Getting started
[Behave documentaion](http://pythonhosted.org/behave/)
[Ansible API](http://docs.ansible.com/developing_api.html)
See product documentation for application APIs

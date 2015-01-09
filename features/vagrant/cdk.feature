Feature: test CDK

# set dynamic hosts
Background: vagrant hosts are discovered
      Given "cihosts" hosts from dynamic inventory

  Scenario: Test vagrant-registry plugin
      Given vagrant plugin "vagrant-registration" is installed
        and vagrant plugin "vagrant-registration" is verified

  Scenario: Test install CDK
      Given Clone CDK from "https://github.com/RHELDevelop/cdk.git"

  Scenario Outline: test boxes
      Given vagrant box "<box>" is already installed
       When Vagrantfile is linked
        and vagrant up
       Then vagrant connect to "vagrant_guest"
        and vagrant "vagrant_guest" is auto-subscribed
        and vagrant "vagrant_guest" is destroyed
        and vagrant "vagrant_guest" is unsubscribed and unregistered

  Examples: vagrant boxes
      | box                 |
      | rhel-7.0            |
      | rhel-atomic-7.0     |


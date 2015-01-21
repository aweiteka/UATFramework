Feature: test vagrant-registration plugin based on source

  # set dynamic hosts
  Background: vagrant hosts are discovered
    Given "cihosts" hosts from dynamic inventory
    and vagrant plugin is "vagrant-registration"

  #assumes that the slave has the build requirements for a plugin
  Scenario: Get and build vagrant-registration plugin
    Given vagrant is installed
    and vagrant plugin build dependencies are installed
    and source of the plugin is cloned from "https://github.com/whitel/vagrant-registration.git"
    and bundler has been used to install ruby dependencies
    When vagrant plugin is built
    Then local "vagrant-registration" gem is successfully installed

  Scenario: Test install CDK
      Given Clone CDK from "https://github.com/RHELDevelop/cdk.git"

  @slow
  Scenario Outline: test boxes
      Given vagrant box "<box>" is already installed
       When Vagrantfile is linked
        and vagrant up
       Then vagrant connect to "vagrant_guest"
        and vagrant "vagrant_guest" is auto-subscribed
        and vagrant "vagrant_guest" is destroyed
#        and vagrant "vagrant_guest" is unsubscribed and unregistered

  Examples: vagrant boxes
      | box                 |
      | rhel-7.0            |
      | rhel-atomic-7.0     |


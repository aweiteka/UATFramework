Feature: test vagrant-registration plugin installed from rubygems.org

  # set dynamic hosts
  Background: vagrant hosts are discovered
    Given "cihosts" hosts from dynamic inventory
    and vagrant plugin is "vagrant-registration"

  #assumes that the slave has the build requirements for a plugin
  Scenario: Install vagrant-registration from rubygems.org
    Given vagrant is installed
    and install vagrant plugin
    Then vagrant plugin is verified as installed

  Scenario: Test install CDK
      Given clone CDK from "https://github.com/RHELDevelop/cdk.git"

  @slow
  Scenario Outline: Test registration on various box types
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


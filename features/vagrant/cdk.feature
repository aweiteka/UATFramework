Feature: RHEL on Vagrant

  Scenario: Test vagrant-registry plugin
      Given vagrant-registration plugin is installed
        and vagrant-registration plugin is verified
        and vagrant box "rhel-7.0" is already installed
       When Vagrantfile is linked
        and vagrant up
       Then connect to "vagrant_guest"
        and "vagrant_guest" is auto-subscribed
        and "vagrant_guest" is destroyed
        and subscription is removed

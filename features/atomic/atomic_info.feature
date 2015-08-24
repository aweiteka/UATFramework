@atomic
Feature: Atomic info test for new upgrade tree
    Describes display label information about a local and remote image

Background: Atomic hosts are discovered
      Given "all" hosts from dynamic inventory

  @env_check
  Scenario: 1. Host provisioned and subscribed
      Given "all" host
       When "all" host is auto-subscribed to "stage"
       Then subscription status is ok on "all"
        and "1" entitlement is consumed on "all"

  Scenario: 2. 'atomic host upgrade' is successful
      Given there is "1" atomic host tree deployed
       When atomic host upgrade is successful
       Then wait "30" seconds for "all" to reboot
       Then there is "2" atomic host tree deployed

  Scenario: 3. Build a new image with new tag from Dockerfile
       When docker build an image with tag "scratch_test" from "https://raw.githubusercontent.com/projectatomic/atomic/master/tests/test-images/Dockerfile.2"
       Then Check whether "scratch_test" is installed

  Scenario: 4. Display label information about a local image
       When Display LABEL information about an image "scratch_test"
       Then Check LABEL "Name: atomic-test-2" information for an image

  Scenario: 5. Display label information about a remote image
       When Display LABEL information about a "remote" image "rhel7"
       Then Check LABEL "Vendor: Red Hat, Inc." information for an image

  Scenario: 6. Remove specified image
       When Remove "scratch_test" from system
       Then Check whether "scratch_test" is removed from system

  @clean_up
  Scenario: 7. Unregister
       Then "all" host is unsubscribed and unregistered
        and subscription status is unknown on "all"

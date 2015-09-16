@atomic
Feature: Atomic images test for new upgrade tree
    Describes listing locally installed images and removing all dangling images on your system

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

  Scenario: 3. Pull latest image from repository
      Given List all locally installed container images
       When atomic update latest "centos" from repository
       Then Check whether "centos" is installed

  Scenario: 4. Build a new image from Dockerfile
       When docker build an image from "https://raw.githubusercontent.com/projectatomic/atomic/master/tests/test-images/Dockerfile.1"
       Then Check whether dangling images exist

  Scenario: 5. Remove dangling images
       When Remove all dangling images
       Then Check whether dangling images do not exist

  Scenario: 6. Remove specified image
       When Remove "centos" from system
       Then Check whether "centos" is removed from system

  @clean_up
  Scenario: 7. Unregister
       Then "all" host is unsubscribed and unregistered
        and subscription status is unknown on "all"

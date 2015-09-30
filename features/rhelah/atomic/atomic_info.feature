@atomic @host_subscribed @ah_upgrade
Feature: Atomic info test for new upgrade tree
    Describes display label information about a local and remote image

Background: Atomic hosts are discovered
      Given "all" hosts can be pinged

  Scenario: 1. Build a new image with new tag from Dockerfile
       When docker build an image with tag "scratch_test" from "https://raw.githubusercontent.com/projectatomic/atomic/master/tests/test-images/Dockerfile.2"
       Then Check whether "scratch_test" is installed

  Scenario: 2. Display label information about a local image
       When Display LABEL information about an image "scratch_test"
       Then Check LABEL "Name: atomic-test-2" information for an image

  Scenario: 3. Display label information about a remote image
       When Display LABEL information about a "remote" image "rhel7"
       Then Check LABEL "Vendor: Red Hat, Inc." information for an image

  Scenario: 4. Remove specified image
       When Remove "scratch_test" from system
       Then Check whether "scratch_test" is removed from system

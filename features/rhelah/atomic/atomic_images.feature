@atomic @host_subscribed @ah_upgrade
Feature: Atomic images test for new upgrade tree
    Describes listing locally installed images and removing all dangling images on your system

Background: Atomic hosts are discovered
      Given "all" hosts can be pinged

  Scenario: 1. Pull latest image from repository
      Given List all locally installed container images
       When atomic update latest "centos" from repository
       Then Check whether "centos" is installed

  Scenario: 2. Build a new image from Dockerfile
       When docker build an image from "https://raw.githubusercontent.com/projectatomic/atomic/master/tests/test-images/Dockerfile.1"
       Then Check whether dangling images exist

  Scenario: 3. Remove dangling images
       When Remove all dangling images
       Then Check whether dangling images do not exist

  Scenario: 4. Remove specified image
       When Remove "centos" from system
       Then Check whether "centos" is removed from system

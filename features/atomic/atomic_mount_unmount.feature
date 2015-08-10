@atomic
Feature: Atomic mount and unmount test for new upgrade tree
    Describes atomic mount/unmount container and image to specified directory

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

  Scenario: 3. docker pull image
      Given "docker" is already running on "all"
       When docker pull "busybox"

  Scenario: 4. mount image to a specified directory
       When atomic mount "image" to a specified "/mnt"
       Then check whether atomic mount point "/var/mnt" exists

  Scenario: 5. unmount image previously mounted
       When atomic unmount image from previous "/mnt"
       Then check whether atomic mount point "/var/mnt" does not exist

  Scenario: 6. docker run busybox with detach mode
       When docker run "busybox" detach mode with "/usr/bin/top -b"
       Then check whether there is a running container

  Scenario: 7. mount running container to a specified directory
       When atomic mount "container" to a specified "/mnt"
       Then check whether atomic mount point "/var/mnt" exists

  Scenario: 8. unmount container previously mounted
       When atomic unmount container from previous "/mnt"
       Then check whether atomic mount point "/var/mnt" does not exist

  Scenario: 9. atomic stop previous running container
       When atomic stop container

  Scenario: 10. remove docker image
       Then remove docker image "busybox"

  @clean_up
  Scenario: 11. Unregister
       Then "all" host is unsubscribed and unregistered
        and subscription status is unknown on "all"

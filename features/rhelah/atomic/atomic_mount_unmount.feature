@atomic @host_subscribed @ah_upgrade
Feature: Atomic mount and unmount test for new upgrade tree
    Describes atomic mount/unmount container and image to specified directory

Background: Atomic hosts are discovered
      Given "all" hosts can be pinged

  Scenario: 1. docker pull image
      Given "docker" is already running on "all"
       When docker pull "busybox"

  Scenario: 2. mount image to a specified directory
       When atomic mount "image" to a specified "/mnt"
       Then check whether atomic mount point "/var/mnt" exists

  Scenario: 3. unmount image previously mounted
       When atomic unmount image from previous "/mnt"
       Then check whether atomic mount point "/var/mnt" does not exist

  Scenario: 4. docker run busybox with detach mode
       When docker run "busybox" detach mode with "/usr/bin/top -b"
       Then check whether there is a running container

  Scenario: 5. mount running container to a specified directory
       When atomic mount "container" to a specified "/mnt"
       Then check whether atomic mount point "/var/mnt" exists

  Scenario: 6. unmount container previously mounted
       When atomic unmount container from previous "/mnt"
       Then check whether atomic mount point "/var/mnt" does not exist

  Scenario: 7. atomic stop previous running container
       When atomic stop container

  Scenario: 8. remove docker image
       Then remove docker image "busybox"

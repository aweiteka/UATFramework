@atomic @host_subscribed @ah_upgrade
Feature: Atomic host sanity test
    Describes the basic 'atomic host' command test

Background: Atomic hosts are discovered
      Given "all" hosts can be pinged

  @pull_image
  Scenario: 1. Pull latest image from repository
      Given List all locally installed container images
       When atomic update latest "centos" from repository
       Then Check whether "centos" is installed

  @mount_image_to_path
  Scenario: 2. mount image to a specified directory
       When atomic mount "image" to a specified "/mnt"
       Then check whether atomic mount point "/var/mnt" exists

  @unmount_image_from_path
  Scenario: 3. unmount image previously mounted
       When atomic unmount image from previous "/mnt"
       Then check whether atomic mount point "/var/mnt" does not exist

  @run_container_in_bg
  Scenario: 4. docker run busybox with detach mode
       When docker run "centos" detach mode with "top -b"
       Then check whether there is a running container

  @mount_container_to_path
  Scenario: 5. mount running container to a specified directory
       When atomic mount "container" to a specified "/mnt"
       Then check whether atomic mount point "/var/mnt" exists

  @unmount_container_from_path
  Scenario: 6. unmount container previously mounted
       When atomic unmount container from previous "/mnt"
       Then check whether atomic mount point "/var/mnt" does not exist

  @stop_container
  Scenario: 7. atomic stop previous running container
       When atomic stop container

  @build_dangling_image
  Scenario: 8. Build a new image from Dockerfile
       When docker build an image from local "Dockerfile.1"
       Then Check whether dangling images exist

  @remove_dangling_image
  Scenario: 9. Remove dangling images
       When Remove all dangling images
       Then Check whether dangling images do not exist

  @build_label_image
  Scenario: 10. Build a new image from Dockerfile
       When docker build an image with tag "centos_label" from local "Dockerfile.1"
       Then Check whether "centos_label" is installed

  @check_image_name_version
  Scenario: 11. Display image label of name version release
       When Display "centos_label" "atomic-test-1" of name version release

  @read_label_install_in_image
  Scenario: 12. Read the LABEL INSTALL field in the container image
       When Read the LABEL INSTALL "I am the install label." field in the container "centos_label"

  @build_info_image
  Scenario: 13. Build a new image with new tag from Dockerfile
       When docker build an image with tag "scratch_test" from local "Dockerfile.2"
       Then Check whether "scratch_test" is installed

  @check_local_image_label
  Scenario: 14. Display label information about a local image
       When Display LABEL information about an image "scratch_test"
       Then Check LABEL "Name: atomic-test-2" information for an image

  @check_remote_image_label
  Scenario: 15. Display label information about a remote image
       When Display LABEL information about a "remote" image "rhel7"
       Then Check LABEL "Vendor: Red Hat, Inc." information for an image

  @remove_built_info_image
  Scenario: 16. Remove scratch_test image
       When Remove "scratch_test" from system
       Then Check whether "scratch_test" is removed from system

  @remove_built_label_image
  Scenario: 17. Remove centos_label image
       When Remove "centos_label" from system
       Then Check whether "centos_label" is removed from system

  @remove_pulled_image
  Scenario: 18. Remove centos image
       Then remove docker image "centos"
         and Check whether "centos" is removed from system

  @rollback_host
  Scenario: 19. Rollback to the original deployment
      Given there is "2" atomic host tree deployed
        and the original atomic version has been recorded
       When atomic host rollback is successful
        and wait "60" seconds for "all" to reboot
       Then the current atomic version should not match the original atomic version

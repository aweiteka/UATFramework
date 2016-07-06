@atomic @host_subscribed @ah_upgrade
Feature: Atomic host sanity test
    Describes the basic 'atomic host' command test

Background: Atomic hosts are discovered
      Given "all" hosts can be pinged

  @pull_centos_image
  Scenario: 1. Pull latest centos image from repository
       When atomic update latest "centos" from repository
       Then Check whether "centos" is installed

  @mount_image_to_path
  Scenario: 2. mount image to a specified directory
       When atomic mount image "centos" to a specified "/mnt"
       Then check whether mount option "/var/mnt" exists

  @unmount_image_from_path
  Scenario: 3. unmount image previously mounted
       When atomic unmount image from previous "/mnt"
       Then check whether mount option "/var/mnt" does not exist

  @compare_the_same_rpm_image
  Scenario: 4. Compare the RPMs in 2 same images
       When Compare the RPMs between "centos" and "centos"
       Then check whether "/sysroot/tmp" does not exist

  @run_container_in_bg
  Scenario: 5. docker run centos with detach mode
       When docker run "centos" in detach mode with "mount_test" "top -b"
       Then find latest created container by name "mount_test"

  @mount_container_to_path
  Scenario: 6. mount running container by name to a specified directory
       When atomic mount container "mount_test" to a specified "/mnt"
       Then check whether mount option "/var/mnt" exists

  @unmount_container_from_path
  Scenario: 7. unmount container previously mounted
       When atomic unmount container from previous "/mnt"
       Then check whether mount option "/var/mnt" does not exist

  @stop_container
  Scenario: 8. atomic stop previous running container
       When atomic stop container "mount_test"

  @build_dangling_image
  Scenario: 9. Build a new image from Dockerfile
       When docker build an image from local "Dockerfile.1"
       Then Check whether dangling images exist

  @remove_dangling_image
  Scenario: 10. Remove dangling images
       When Remove all dangling images
       Then Check whether dangling images do not exist

  @build_label_image
  Scenario: 11. Build a new image from Dockerfile
       When docker build an image with tag "centos_label" from local "Dockerfile.1"
       Then Check whether "centos_label" is installed

  @check_image_name_version
  Scenario: 12. Display image label of name version release
       When Display "centos_label" "atomic-test-1" of name version release

  @read_label_install_in_image
  Scenario: 13. Read the LABEL INSTALL field in the container image
       When Read the LABEL INSTALL "I am the install label." field in the container "centos_label"

  @build_apache_image
  Scenario: 14. Build a apache image from Dockerfile
       When docker build an image with tag "centos/apache" from local "Dockerfile.3"
       Then Check whether "centos/apache" is installed

  @compare_the_different_rpm_image
  Scenario: 15. Compare the RPMs in 2 different images
       When Compare the RPMs with "-nr" between "centos" and "centos/apache"
       Then check whether "/sysroot/tmp" does not exist

  @pull_busybox_image
  Scenario: 16. Pull latest image from repository
      Given List all locally installed container images
       When atomic update latest "busybox" from repository
       Then Check whether "busybox" is installed

  @compare_the_image_not_rpm_based
  Scenario: 17. Compare the RPMs in 2 no RPMs images
       When Compare the RPMs between "busybox" and "busybox" are "no" RPMs based
       Then check whether "/sysroot/tmp" does not exist

  @compare_the_image_with_arguments_1
  Scenario: 18. Compare the RPMs with -nr --json options
       When Compare the RPMs with "-nr --json" between "centos" and "centos/apache"
       Then check whether "/sysroot/tmp" does not exist

  @compare_the_image_with_arguments_2
  Scenario: 19. Compare the RPMs with -v --names-only options
       When Compare the RPMs with "-v --names-only" between "centos" and "centos/apache"
       Then check whether "/sysroot/tmp" does not exist

  @build_info_image
  Scenario: 20. Build a new image with new tag from Dockerfile
       When docker build an image with tag "scratch_test" from local "Dockerfile.2"
       Then Check whether "scratch_test" is installed

  @check_local_image_label
  Scenario: 21. Display label information about a local image
       When Display LABEL information about an image "scratch_test"
       Then Check LABEL "Name: atomic-test-2" information for an image

  @check_remote_image_label
  Scenario: 22. Display label information about a remote image
       When Display LABEL information about a "remote" image "registry.access.redhat.com/rhel7"
       Then Check LABEL "Vendor: Red Hat, Inc." information for an image

  @remove_all_containers
  Scenario: 23. Remove all of containers
       When docker remove all of containers

  @remove_built_info_image
  Scenario: 24. Remove scratch_test image
       When Remove "scratch_test" from system
       Then Check whether "scratch_test" is removed from system

  @remove_built_label_image
  Scenario: 25. Remove centos_label image
       When Remove "centos_label" from system
       Then Check whether "centos_label" is removed from system

  @remove_pulled_busybox_image
  Scenario: 26. Remove busybox image
       Then remove docker image "busybox"
        and Check whether "busybox" is removed from system

  @remove_built_apache_image
  Scenario: 27. Remove apache image
       Then remove docker image "centos/apache"
        and Check whether "centos/apache" is removed from system

  @remove_pulled_centos_image
  Scenario: 28. Remove centos image
       Then remove docker image "centos"
        and Check whether "centos" is removed from system

  @rollback_host
  Scenario: 29. Rollback to the original deployment
      Given there is "2" atomic host tree deployed
        and the original atomic version has been recorded
       When atomic host rollback is successful
        and wait "60" seconds for "all" to reboot
       Then the current atomic version should not match the original atomic version

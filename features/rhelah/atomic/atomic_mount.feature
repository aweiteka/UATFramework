@atomic @host_subscribed @ah_upgrade
Feature: Atomic mount sanity test
    Describes the basic 'atomic mount' command test

Background: Atomic hosts are discovered
      Given "all" hosts can be pinged

  @pull_busybox_image
  Scenario: 1. Pull latest busybox image from repository
       When atomic update latest "busybox" from repository
       Then check whether "busybox" is installed

  @mount_image_without_option
  Scenario: 2. mount image to a specified directory
       When atomic mount image "busybox" to a specified "/mnt"
       Then check whether mount option "/var/mnt" exists

  @unmount_without_option_image
  Scenario: 3. unmount busybox image previously mounted
       When atomic unmount image from previous "/mnt"
       Then check whether mount option "/var/mnt" does not exist

  @mount_image_with_live_option
  Scenario: 4. mount live image to a specified directory
       When atomic mount image "busybox" with "--live" to a specified "/mnt"

  @pull_rhel7_image
  Scenario: 5. Pull latest rhel7 image from repository
       When atomic update latest "registry.access.redhat.com/rhel7" from repository
       Then check whether "rhel7" is installed

  @run_rhel7_in_bg
  Scenario: 6. docker run rhel7 with detach mode
       When docker run "registry.access.redhat.com/rhel7" in detach mode with "mount_test" "top -b"
       Then find latest created container by name "mount_test"

  @mount_container_without_option
  Scenario: 7. mount running container by name to a specified directory
       When atomic mount container "mount_test" to a specified "/mnt"
       Then check whether mount option "/var/mnt" exists
        and check "mount_test" "/var/mnt"

  @pull_rsyslog_image
  Scenario: 8. Pull latest rhel7/rsyslog image from repository
       When atomic update latest "registry.access.redhat.com/rhel7/rsyslog" from repository
       Then check whether "rsyslog" is installed

  @run_rsyslog1_with_command
  Scenario: 9. docker run rhel7/rsyslog with detach mode and attach previous mount point into it
       When docker run "registry.access.redhat.com/rhel7/rsyslog" "--volume /var/mnt:/mnt" in detach mode "false" with "C1" "ls /mnt" and ignore error "true"
       Then check if "Permission denied" is in result of docker run

  @unmount_without_option_container
  Scenario: 10. unmount container previously mounted
       When atomic unmount container from previous "/mnt"
       Then check whether mount option "/var/mnt" does not exist

  @mount_container_with_live_option
  Scenario: 11. mount running container with live option
       When atomic mount container "mount_test" with "--live" to a specified "/mnt"
       Then check whether mount option "/var/mnt" exists
        and check "mount_test" "/var/mnt" "--live"

  @run_rsyslog2_with_command
  Scenario: 12. docker run rhel7/rsyslog with detach mode and attach previous mount point into it
       When docker run "registry.access.redhat.com/rhel7/rsyslog" "--volume /var/mnt:/mnt" in detach mode "false" with "C2" "ls /mnt" and ignore error "true"
       Then check if "Permission denied" is in result of docker run

  @unmount_live_container
  Scenario: 13. unmount live container previously mounted
       When atomic unmount container from previous "/mnt"
       Then check whether mount option "/var/mnt" does not exist

  @mount_container_with_shared_option
  Scenario: 14. mount running container with shared option
       When atomic mount container "mount_test" with "--shared" to a specified "/mnt"
       Then check whether mount option "/var/mnt" exists
        and check "mount_test" "/var/mnt" "--shared"

  @run_rsyslog3_with_command
  Scenario: 15. docker run rhel7/rsyslog with detach mode and attach previous mount point into it
       When docker run "registry.access.redhat.com/rhel7/rsyslog" "--volume /var/mnt:/mnt" in detach mode "false" with "C3" "ls -Z /mnt" and ignore error "true"
       Then check if "system_u:object_r:usr_t:s0" is in result of docker run

  @unmount_shared_container
  Scenario: 16. unmount shared container previously mounted
       When atomic unmount container from previous "/mnt"
       Then check whether mount option "/var/mnt" does not exist

  @stop_container
  Scenario: 17. atomic stop previous running container
       When atomic stop container "mount_test"

  @remove_all_containers
  Scenario: 18. Remove all of containers
       When docker remove all of containers

  @remove_all_images
  Scenario: 19. Remove all of containers
       When docker remove all of images

  @rollback_host
  Scenario: 20. Rollback to the original deployment
      Given there is "2" atomic host tree deployed
        and the original atomic version has been recorded
       When atomic host rollback is successful
        and wait "60" seconds for "all" to reboot
       Then the current atomic version should not match the original atomic version

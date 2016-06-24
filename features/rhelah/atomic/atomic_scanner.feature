@atomic @host_subscribed @ah_upgrade
Feature: Atomic scanner test
    Describes the basic 'atomic scan' command test

Background: Atomic hosts are discovered
      Given "all" hosts can be pinged

  @list_default_scanners
  Scenario: 1. List default scanners
       When List default scanners
       Then find specified scanner "rhel7/openscap"

  @pull_atomic_scan_openscap_image
  Scenario: 2. Pull latest openscap image from repository
       When atomic update latest "docker.io/fedora/atomic_scan_openscap" from repository
       Then Check whether "atomic_scan_openscap" is installed

  @atomic_install_openscap_image
  Scenario: 3. Execute openscap image install method
       When Execute "docker.io/fedora/atomic_scan_openscap" install method

  @list_current_scanners
  Scenario: 4. List available scanners
       When List available scanners
       Then find specified scanner "rhel7/openscap"
        and find specified scanner "atomic_scan_openscap"

  @pull_centos_image
  Scenario: 5. Pull latest centos image from repository
       When atomic update latest "centos" from repository
       Then Check whether "centos" is installed

  @scan_centos_image
  Scenario: 6. Scanning centos image
       When Scan "centos" with "atomic_scan_openscap" and "cve" "--verbose"
       Then Check "not supported" in scanner report
        and check whether "/run/atomic" does not exist

  @pull_rhel7_image
  Scenario: 7. Pull latest rhel7 image from repository
       When atomic update latest "registry.access.redhat.com/rhel7" from repository
       Then Check whether "rhel7" is installed

  @scan_rhel7_image
  Scenario: 8. Scanning rhel7 image
       When Scan "registry.access.redhat.com/rhel7" with "atomic_scan_openscap" and "cve" "--verbose"
       Then Check "issues were found" in scanner report
        and check whether "/run/atomic" does not exist

  @scan_all_images
  Scenario: 9. Scanning all of images
       When Scan "--images" with "atomic_scan_openscap" and "cve" "--verbose"
       Then Check "issues were found" in scanner report
        and Check "not supported" in scanner report
        and check whether "/run/atomic" does not exist

  @run_container1_in_bg
  Scenario: 10. docker run container1 with detach mode
       When docker run "centos" in detach mode with "C1" "top -b"
       Then find latest created container by name "C1"

  @run_container2_in_bg
  Scenario: 11. docker run container2 with detach mode
       When docker run "rhel7" in detach mode with "C2" "top -b"
       Then find latest created container by name "C2"

  @scan_containers
  Scenario: 12. scan containers
       When Scan "--containers" with "atomic_scan_openscap" and "cve" "--verbose"
       Then Check "issues were found" in scanner report
        and Check "not supported" in scanner report
        and check whether "/run/atomic" does not exist

  @scan_images_and_containers
  Scenario: 13. scan all of images and containers
       When Scan "--all" with "atomic_scan_openscap" and "cve" "--verbose"
       Then Check "issues were found" in scanner report
        and Check "not supported" in scanner report
        and check whether "/run/atomic" does not exist

  @stop_container1
  Scenario: 14. atomic stop previous running container1
       When atomic stop container "C1"

  @stop_container2
  Scenario: 15. atomic stop previous running container2
       When atomic stop container "C2"

  @remove_all_containers
  Scenario: 16. Remove all of containers
       When docker remove all of containers

  @remove_all_images
  Scenario: 17. Remove all of containers
       When docker remove all of images

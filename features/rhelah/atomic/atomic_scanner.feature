#@atomic @host_subscribed @ah_upgrade
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
       When Scan "centos" with "openscap" and "cve" "--verbose"
       Then Check "not supported" in scanner report
        and check whether "/run/atomic" does not exist

  @pull_fedora_image
  Scenario: 7. Pull latest fedora image from repository
       When atomic update latest "fedora" from repository
       Then Check whether "fedora" is installed

  @scan_fedora_image
  Scenario: 8. Scanning fedora image
       When Scan "fedora" with "atomic_scan_openscap" and "cve" "--verbose"
       Then Check "not supported" in scanner report
        and check whether "/run/atomic" does not exist

  @remove_atomic_scan_openscap_image
  Scenario: 9. Remove atomic_scan_openscap image
       Then remove docker image "docker.io/fedora/atomic_scan_openscap"
        and Check whether "atomic_scan_openscap" is removed from system

  @pull_rhel7_image
  Scenario: 10. Pull latest rhel7 image from repository
       When atomic update latest "registry.access.redhat.com/rhel7" from repository
       Then Check whether "rhel7" is installed

  @scan_rhel7_image
  Scenario: 11. Scanning rhel7 image
       When Scan "registry.access.redhat.com/rhel7" with "openscap" and "cve" "--verbose"
       Then Check "issues were found" in scanner report
        and check whether "/run/atomic" does not exist

  @scan_all_images
  Scenario: 12. Scanning all of images
       When Scan "--images" with "openscap" and "cve" "--verbose"
       Then Check "issues were found" in scanner report
        and Check "not supported" in scanner report
        and check whether "/run/atomic" does not exist

  @run_container1_in_bg
  Scenario: 13. docker run container1 with detach mode
       When docker run "centos" in detach mode with "C1" "top -b"
       Then find latest created container by name "C1"

  @run_container2_in_bg
  Scenario: 14. docker run container2 with detach mode
       When docker run "rhel7" in detach mode with "C2" "top -b"
       Then find latest created container by name "C2"

  @scan_containers
  Scenario: 15. scan containers
       When Scan "--containers" with "openscap" and "cve" "--verbose"
       Then Check "issues were found" in scanner report
        and Check "not supported" in scanner report
        and check whether "/run/atomic" does not exist

  @scan_images_and_containers
  Scenario: 16. scan all of images and containers
       When Scan "--all" with "openscap" and "cve" "--verbose"
       Then Check "issues were found" in scanner report
        and Check "not supported" in scanner report
        and check whether "/run/atomic" does not exist

  @stop_container1
  Scenario: 17. atomic stop previous running container1
       When atomic stop container "C1"

  @stop_container2
  Scenario: 18. atomic stop previous running container2
       When atomic stop container "C2"

  @remove_all_containers
  Scenario: 19. Remove all of containers
       When docker remove all of containers

  @remove_centos_image
  Scenario: 20. Remove centos image
       Then remove docker image "centos"
        and Check whether "centos" is removed from system

  @remove_fedora_image
  Scenario: 21. Remove fedora image
       Then remove docker image "fedora"
        and Check whether "fedora" is removed from system

  @pull_rsyslog_image
  Scenario Outline: 22. Pull latest <image> image from repository
       When atomic update latest "registry.access.redhat.com/<image>" from repository
        and Scan "registry.access.redhat.com/<image>" with "atomic_scan_openscap" and "cve" "--verbose"
       Then Check whether "<image>" is installed
        and Check "issues were found" in scanner report
        and check whether "/run/atomic" does not exist
   Examples:Images
     | image                           |
     | rhel6                           |
     | rhel7/rsyslog                   |
     | rhel7/sadc                      |
     | rhel7/sssd                      |
     | rhel7/etcd                      |
     | rhel7/kubernetes-apiserver      |
     | rhel7/kubernetes-scheduler      |
     | rhel7/kubernetes-controller-mgr |
     | rhel7/pod-infrastructure        |
     | rhel7/cockpit-ws                |
     | rhel7/rhel-tools                |
 
  @remove_all_images
  Scenario: 23. Remove all of images
       When docker remove all of images

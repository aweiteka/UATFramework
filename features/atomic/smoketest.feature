Feature: Atomic host smoke test
  Describes minimum functionality for Docker and Kubernetes

# set dynamic hosts
Background: Atomic hosts are discovered
      Given "cihosts" hosts from dynamic inventory

  Scenario: Host provisioned and subscribed
      Given "cihosts" host
       When "cihosts" host is auto-subscribed
       Then subscription status is ok on "cihosts"
        and "1" entitlement is consumed on "cihosts"

  Scenario: Docker smoke test
      Given "docker" is already installed on "cihosts"
        and "docker" is already running on "cihosts"
       When image "rhel7" is pulled on "cihosts"
       Then rpm "bind" is installed in "rhel7" on "cihosts"

  Scenario: Kubernetes smoke test
      Given "kubernetes" is already installed on "cihosts"
        and "etcd" is already installed on "cihosts"
        and "kubelet" is started on "cihosts"
        and "etcd" is started on "cihosts"
       When application "guestbook" is run from "cihosts"
       Then application "guestbook" is verified


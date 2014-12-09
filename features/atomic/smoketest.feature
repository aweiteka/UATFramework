Feature: Atomic host smoke test
  Describes minimum functionality for Docker and Kubernetes
  TODO: OSTree upgrade and rollback

  Background: Single atomic host is provisioned
      Given "atomic" host
       Then "atomic" host is auto-subscribed

  Scenario: Host subscribed
      Given subscription status is ok on "atomic"
       Then "1" entitlement is consumed on "atomic"

  Scenario: Docker smoke test
      Given "docker" is already installed on "atomic"
        and "docker" is already running on "atomic"
       When container "rhel7" is run on "atomic"
       Then "mycontainer" rpms are updated using host subscription
        and rpm "myrpm" is installed in "mycontainer"

  Scenario: Kubernetes smoke test
      Given "kubernetes" is already installed on "atomic"
        and "etcd" is already installed on "atomic"
        and "kubelet" is started on "atomic"
        and "etcd" is started on "atomic"
       When pod "mypod" is run from "atomic"
       Then service "mypod" is verified

  Scenario: dev
      Given "puppet" is already running on "ATOMIC"
        and "tftp" is already installed on "atomic"
       Then service "asdf" is verified

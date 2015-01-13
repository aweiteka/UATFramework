Feature: Atomic host smoke test
  Describes minimum functionality for Docker and Kubernetes

# set dynamic hosts
Background: Atomic hosts are discovered
      Given "cihosts" hosts from dynamic inventory

  Scenario: 1. Host provisioned and subscribed
      Given "cihosts" host
       When "cihosts" host is auto-subscribed to "stage"
       Then subscription status is ok on "cihosts"
        and "1" entitlement is consumed on "cihosts"

  Scenario: 2. Docker smoke test
      Given "docker" is already installed on "cihosts"
        and "docker" is already running on "cihosts"
       When image "rhel7" is pulled on "cihosts"
       Then rpm "bind" is installed in "rhel7" on "cihosts"

  Scenario Outline: 3. Kubernetes services
      Given "kubernetes" is already installed on "cihosts"
        and "etcd" is already installed on "cihosts"
       Then "<service>" is started and enabled on "cihosts"

  Examples: kubernetes services
    | service                 |
    | etcd                    |
    | kube-apiserver          |
    | kube-controller-manager |
    | kube-scheduler          |
    | kube-proxy              |
    | kubelet                 |

  Scenario: 4. kubectl smoke test
       Given "0" pods on "cihosts"
         and "0" services on "cihosts"

  Scenario: 5. Unregister
       Then "cihosts" host is unsubscribed and unregistered

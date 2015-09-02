@kube
Feature: Atomic cluster smoke test
  Describes minimum functionality for Kubernetes on a multi-node Atomic cluster
  Cluster is configured using ansible script in upstream kubernetes/contrib repo

  Scenario: 1. kubectl API smoke test
       Given "masters" hosts from dynamic inventory
         and "0" "pods" are running
         and "2" "nodes" are running
         and "1" "services" are running
         and nodes are ready

  Scenario: 2. pod communication across nodes
       Given "masters" hosts from dynamic inventory
        When the "sleeper" pod is running on node "1"
         and the "sleeper" pod is running on node "2"
        Then the "sleeper-1" pod can ping the "sleeper-2" pod

  Scenario: 3. DNS service resolution from pods
       Given "masters" hosts from dynamic inventory
        When the "sleeper" pod is running on node "1"
         and the "sleeper" pod is running on node "2"
         and the "httpd" service exists
        Then the "sleeper-1" pod can resolve the "httpd" service
         and the "sleeper-2" pod can resolve the "httpd" service

  Scenario: 4. service reachability from pods
       Given "masters" hosts from dynamic inventory
        When the "sleeper" pod is running on node "1"
         and the "sleeper" pod is running on node "2"
         and the "httpd" pod is running on node "1"
         and the "httpd" service exists
        Then the "sleeper-1" pod can reach the httpd service
         and the "sleeper-2" pod can reach the httpd service

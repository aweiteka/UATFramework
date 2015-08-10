@kube
Feature: Atomic cluster smoke test
  Describes minimum functionality for Kubernetes on a multi-node Atomic cluster
  Cluster is configured using contrib/ansible script in upstream kube repo

  Scenario: 1. kubectl API smoke test
       Given "masters" hosts from dynamic inventory
         and "0" "pods" are running
         and "2" "nodes" are running
         and "1" "services" are running

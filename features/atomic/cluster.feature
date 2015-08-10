@kube
Feature: Atomic cluster smoke test
  Describes minimum functionality for Kubernetes on a multi-node Atomic cluster
  Cluster is configured using https://github.com/eparis/kubernetes-ansible

  Scenario: 1. kubectl API smoke test
       Given "masters" hosts from dynamic inventory
         and "1" "pods" are running
         and "2" "minions" are running
         and "3" "services" are running


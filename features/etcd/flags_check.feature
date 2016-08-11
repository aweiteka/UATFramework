@atomic @etcd
Feature: Etcd flags check test
    Describes the basic check for etcd flags in etcd.conf and etcd --help

Background: Atomic hosts are discovered
      Given "all" hosts can be pinged

Scenario: 1. Check etcd flags in etcd.conf and etcd --help
     Given file "etcd_conf_file" is exist on "server"
       And "etcd" is already installed on "server"
      Then Compare etcd flags from help output and etcd.conf

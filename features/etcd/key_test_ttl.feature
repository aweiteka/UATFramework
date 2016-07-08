@atomic @etcd @services_status
Feature: Etcd flags check test
    Describes the basic check for etcd flags in etcd.conf and etcd --help

Background: Atomic hosts are discovered
      Given "server" hosts can be pinged
       When services "etcd" status is "active" on "server"
       Then init etcd client on "server"

Scenario: Check key value with ttl
     Given "put" etcd "keys" "message" on "server" with "ttl=5 value=hello"
      Then check etcd keys on "server" in "6"s

Scenario: Check dir with ttl
    Given "put" etcd "keys" "foo2" on "server" with "dir=True"
      And "put" etcd "keys" "foo2" on "server" with "query_dir=True query_prevExist=True ttl=5"
     Then check etcd keys on "server" in "6"s

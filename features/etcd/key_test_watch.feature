@atomic @etcd @services_status
Feature: Etcd flags check test
    Describes the basic check for etcd flags in etcd.conf and etcd --help

Background: Atomic hosts are discovered
      Given "server" hosts can be pinged
       When services "etcd" status is "active" on "server"
       Then init etcd client on "server"

Scenario: Watch key message
    Given "watch" etcd key "message" on "server" expect "hello"
      And "put" etcd "keys" "message" on "server" with "value=hello"
     Then check etcd watch output is "hello" and "finished" on "server"

Scenario: Exec-watch key message
    Given "exec-watch" etcd key "message" on "server" expect "hi"
     Then set etcd key "message" with "hi" on "server" for "10" times
      And check etcd watch output is "hi" and "running" on "server"

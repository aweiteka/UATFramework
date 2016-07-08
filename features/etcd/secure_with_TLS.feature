@atomic @etcd
Feature: Etcd flags check test
    Describes the basic check for etcd flags in etcd.conf and etcd --help

Background: Atomic hosts are discovered
      Given "server" hosts can be pinged
        And a set of etcd cluster members:
        |name   |cert-file        |key-file         |listen-client-urls     |advertise-client-urls  |host   |
        |server |/root/server.crt |/root/server.key |https://127.0.0.1:2379 |http://127.0.0.1:2379  |server |
       Then init etcd client on "all"

Scenario: Start etcd server with signed key pair
    Given generate "server" key pair for "127.0.0.1"
      And copy "etcd/server.crt" to "/root/server.crt" in "server"
      And copy "etcd/ca.crt" to "/root/ca.crt" in "server"
      And copy "etcd/server.key" to "/root/server.key" in "server"
     Then start the etcd cluster

Scenario Outline: <action>
     Given "<op>" etcd "<category>" "<key>" on "server" with "<args>"
      Then "<value>" stored in etcd named "<key>" on "server"

Examples: Keys
  |action        |op      |category    |key     |args                                                  |value    |
  |create keys   |put     |keys        |message |value=hello query_prevExist=False ca-file=/root/ca.crt|hello    |
  |set keys      |put     |keys        |message |value=hola  ca-file=/root/ca.crt                      |hola     |
  |update keys   |put     |keys        |message |value=hello query_prevExist=True ca-file=/root/ca.crt |hello    |
  |delete keys   |delete  |keys        |message |ca-file=/root/ca.crt                                  |None     |
  |set keys(new) |put     |keys        |message |value=hola ca-file=/root/ca.crt                       |hola     |
  |delete keys   |delete  |keys        |message |ca-file=/root/ca.crt                                  |None     |

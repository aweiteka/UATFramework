@atomic @etcd @services_status
Feature: Etcd flags check test
    Describes the basic check for etcd flags in etcd.conf and etcd --help

Background: Atomic hosts are discovered
      Given "server" hosts can be pinged
       When services "etcd" status is "active" on "server"
       Then init etcd client on "server"

Scenario: Get etcd version
     Then get etcd version on "server"

Scenario Outline: <action>
     Given "<op>" etcd "<category>" "<key>" on "server" with "<args>"
      Then "<value>" stored in etcd named "<key>" on "server"

Examples: Keys
  |action        |op      |category    |key     |args                             |value    |
  |create keys   |put     |keys        |etcd-t  |value=hello query_prevExist=False|hello    |
  |set keys      |put     |keys        |etcd-t  |value=hola                       |hola     |
  |update keys   |put     |keys        |etcd-t  |value=hello query_prevExist=True |hello    |
  |delete keys   |delete  |keys        |etcd-t  |None                             |None     |
  |set keys(new) |put     |keys        |etcd-t  |value=hola                       |hola     |
  |delete keys   |delete  |keys        |etcd-t  |None                             |None     |
  |create dir    |put     |keys        |foo     |dir=True query_prevExist=False   |True     |
  |set dir       |put     |keys        |foo     |dir=True                         |True     |
  |create keys   |put     |keys        |foo/hi  |value=hello                      |hello    |
  |delete keys   |delete  |keys        |foo/hi  |None                             |None     |
  |delete dir    |delete  |keys        |foo     |query_dir=true                   |None     |

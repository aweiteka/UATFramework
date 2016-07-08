@atomic @etcd
Feature: Etcd flags check test
    Describes the basic check for etcd flags in etcd.conf and etcd --help

Background: Atomic hosts are discovered
      Given "all" hosts can be pinged
        And a set of etcd cluster members:
        |name   |initial-advertise-peer-urls|listen-peer-urls       |listen-client-urls                          |advertise-client-urls   |discovery                                    |host   |
        |infra1 |http://infra1_ip:2380      |http://infra1_ip:2380  |http://infra1_ip:2379,http://127.0.0.1:2379 |http://infra1_ip:2379   |http://server_ip:2379/v2/keys/discovery/uuid |infra1 |
        |infra2 |http://infra2_ip:2380      |http://infra2_ip:2380  |http://infra2_ip:2379,http://127.0.0.1:2379 |http://infra2_ip:2379   |http://server_ip:2379/v2/keys/discovery/uuid |infra2 |
        |infra3 |http://infra3_ip:2380      |http://infra3_ip:2380  |http://infra3_ip:2379,http://127.0.0.1:2379 |http://infra3_ip:2379   |http://server_ip:2379/v2/keys/discovery/uuid |infra3 |
       Then init etcd client on "all"

Scenario: Print out the cluster
    Given create discovery url
     Then start the etcd cluster
       And check etcd cluster members
       And check etcd cluster health

Scenario: Check value in cluster
     Given "put" etcd "keys" "message" on "infra1" with "value=cluster_test"
      Then "cluster_test" stored in etcd named "message" on "infra*"
       And "delete" etcd "keys" "message" on "infra2" with "None"

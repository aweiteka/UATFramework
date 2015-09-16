Feature: Atomic unique machine_id test
    Tests whether /etc/machine_id is unique between two RHEL Atomic Hosts deployments

Background: Atomic hosts are discovered
      Given "host1" hosts from dynamic inventory
	and "host2" hosts from dynamic inventory

  Scenario: 0. /etc/machine-id is unique with each instance of rhelah
       Given machine-id on "host1" is recorded
        and machine-id on "host2" is recorded
       Then check if the machine-id on "host1" and "host2" differ

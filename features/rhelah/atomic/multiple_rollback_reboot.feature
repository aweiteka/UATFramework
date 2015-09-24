@host_subscribed @ah_upgrade_no_reboot
Feature:  Verifies that 'atomic host rollback' followed by a reboot can be used multiple times without error

Background: Atomic hosts are discovered
      Given "all" hosts from dynamic inventory
        and "all" hosts can be pinged

  Scenario: 1. Reboot into new deployment
      Given there is "2" atomic host tree deployed
        and the original atomic version has been recorded
       When wait "30" seconds for "all" to reboot
       Then the current atomic version should not match the original atomic version

  Scenario: 2. Rollback and reboot multiple (9) times
      Given there is "2" atomic host tree deployed
       When rollback and reboot occurs multiple times
       Then there is "2" atomic host tree deployed

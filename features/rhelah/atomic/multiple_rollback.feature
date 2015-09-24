@host_subscribed @ah_upgrade_no_reboot
Feature:  Verifies that 'atomic host rollback' can be used multiple times without error

Background: Atomic hosts are discovered
      Given "all" hosts from dynamic inventory
        and "all" hosts can be pinged

  Scenario: 1. Reboot into new deployment
      Given there is "2" atomic host tree deployed
        and the original atomic version has been recorded
       When wait "30" seconds for "all" to reboot
       Then the current atomic version should not match the original atomic version

  Scenario: 2. Rollback multiple (10) times
      Given there is "2" atomic host tree deployed
        and the original atomic version has been recorded
       When rollback occurs multiple times
       Then there is "2" atomic host tree deployed
        and the current atomic version should match the original atomic version

  Scenario: 3. Rollback once more and reboot
      Given there is "2" atomic host tree deployed
        and the original atomic version has been recorded
       When atomic host rollback is successful
        and wait "30" seconds for "all" to reboot
       Then the current atomic version should not match the original atomic version

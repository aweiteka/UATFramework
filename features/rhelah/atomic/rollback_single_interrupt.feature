@host_subscribed @ah_upgrade_no_reboot
Feature:  Verifies that the 'atomic host rollback' can be interrupted
          a single time without error

Background: Atomic hosts are discovered
      Given "all" hosts can be pinged

  Scenario: 1. Reboot into new deployment
      Given there is "2" atomic host tree deployed
        and the original atomic version has been recorded
       When wait "30" seconds for "all" to reboot
       Then the current atomic version should not match the original atomic version

  Scenario: 2. Start rollback process and interrupt 1 times
      Given the rollback interrupt script is present
        and the original atomic version has been recorded
       When the rollback interrupt script is run "1" times
       Then the current atomic version should match the original atomic version

  Scenario: 3. Reboot the system
      Given the original atomic version has been recorded
       When wait "30" seconds for "all" to reboot
       Then the current atomic version should match the original atomic version

  Scenario: 4. Complete the rollback
      Given there is "2" atomic host tree deployed
       When atomic host rollback is successful
       Then there is "2" atomic host tree deployed

  Scenario: 5. Reboot into new deployment
      Given there is "2" atomic host tree deployed
        and the original atomic version has been recorded
       When wait "30" seconds for "all" to reboot
       Then the current atomic version should not match the original atomic version

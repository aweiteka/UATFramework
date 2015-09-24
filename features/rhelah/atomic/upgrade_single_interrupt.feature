@host_subscribed
Feature:  Verifies that the 'atomic host upgrade' can be interrupted
          a single time without error

Background: Atomic hosts are discovered
      Given "all" hosts from dynamic inventory
        and "all" hosts can be pinged

  Scenario: 1. Start upgrade process and interrupt 1 times
      Given the upgrade interrupt script is present
        and the original atomic version has been recorded
       When the upgrade interrupt script is run "1" times
       Then the current atomic version should match the original atomic version

  Scenario: 2. Reboot the system
      Given the original atomic version has been recorded
       When wait "30" seconds for "all" to reboot
       Then the current atomic version should match the original atomic version

  Scenario: 3. Complete the upgrade
      Given there is "1" atomic host tree deployed
       When atomic host upgrade is successful
       Then there is "2" atomic host tree deployed

  Scenario: 4. Reboot into new deployment
      Given there is "2" atomic host tree deployed
        and the original atomic version has been recorded
       When wait "30" seconds for "all" to reboot
       Then the current atomic version should not match the original atomic version

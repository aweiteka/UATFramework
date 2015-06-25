Feature:  Verifies that the 'atomic host rollback' can be interrupted
          a single time without error

Background: Atomic hosts are discovered
      Given "all" hosts from dynamic inventory
        and "all" hosts can be pinged

  Scenario: 1. Host provisioned and subscribed
       When "all" host is auto-subscribed to "stage"
       Then subscription status is ok on "all"
        and "1" entitlement is consumed on "all"

  Scenario: 2. Upgrade to latest release
      Given there is "1" atomic host tree deployed
       When atomic host upgrade is successful
       Then there is "2" atomic host tree deployed

  Scenario: 3. Reboot into new deployment
      Given there is "2" atomic host tree deployed
        and the original atomic version has been recorded
       When wait "30" seconds for "all" to reboot
       Then the current atomic version should not match the original atomic version

  Scenario: 4. Start rollback process and interrupt 10 times
      Given the rollback interrupt script is present
        and the original atomic version has been recorded
       When the rollback interrupt script is run "10" times
       Then the current atomic version should match the original atomic version

  Scenario: 5. Reboot the system
      Given the original atomic version has been recorded
       When wait "30" seconds for "all" to reboot
       Then the current atomic version should match the original atomic version

  Scenario: 6. Complete the rollback
      Given there is "2" atomic host tree deployed
       When atomic host rollback is successful
       Then there is "2" atomic host tree deployed

  Scenario: 7. Reboot into new deployment
      Given there is "2" atomic host tree deployed
        and the original atomic version has been recorded
       When wait "30" seconds for "all" to reboot
       Then the current atomic version should not match the original atomic version

  Scenario: 8. Unregister
       Then "all" host is unsubscribed and unregistered
        and subscription status is unknown on "all"


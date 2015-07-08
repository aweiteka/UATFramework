Feature:  Verifies that 'atomic host rollback' followed by a reboot can be used multiple times without error

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

  Scenario: 4. Rollback and reboot multiple (9) times
      Given there is "2" atomic host tree deployed
       When rollback and reboot occurs multiple times
       Then there is "2" atomic host tree deployed

  Scenario: 5. Unregister
       Then "all" host is unsubscribed and unregistered
        and subscription status is unknown on "all"


Feature:  Verifies that the 'atomic host rollback' can be interrupted
          a single time without error

Background: Atomic hosts are discovered
      Given "all" hosts from dynamic inventory
        And "all" hosts can be pinged

  Scenario: 1. Host provisioned and subscribed
       When "all" host is auto-subscribed to "stage"
       Then subscription status is ok on "all"
        And "1" entitlement is consumed on "all"

  Scenario: 2. Upgrade to latest release
      Given get the number of atomic host tree deployed
       When confirm atomic host tree to old version
        And atomic host upgrade is successful
       Then there is "2" atomic host tree deployed

  Scenario: 3. Reboot into new deployment
      Given there is "2" atomic host tree deployed
        And the original atomic version has been recorded
       When wait "60" seconds for "all" to reboot
       Then the current atomic version should not match the original atomic version

  Scenario: 4. Undeploy the new deployment
      Given there is "2" atomic host tree deployed
       When confirm atomic host tree to old version
       Then undeploy the unselected deployment
       And there is "1" atomic host tree deployed
       And wait "30" seconds for "all" to reboot

  Scenario: 5. Unregister
       Then "all" host is unsubscribed and unregistered
        And subscription status is unknown on "all"


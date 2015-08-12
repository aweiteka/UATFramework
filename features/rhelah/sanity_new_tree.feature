Feature: Atomic host sanity test for new upgrade tree
    Describes tests for upgrade/rollback to/from new ostree

Background: Atomic hosts are discovered
      Given "all" hosts from dynamic inventory
        and "all" host

  Scenario: 1. Subscribe to production
      When "all" host is auto-subscribed to "prod"
       Then subscription status is ok on "all"
        and "1" entitlement is consumed on "all"

  Scenario: 2. 'atomic host upgrade' is successful
      Given there is "1" atomic host tree deployed
       When atomic host upgrade is successful
       Then there is "2" atomic host tree deployed

  Scenario: 3. Reboot into the new deployment
      Given there is "2" atomic host tree deployed
        and the original atomic version has been recorded
       When wait "30" seconds for "all" to reboot
       Then the current atomic version should not match the original atomic version

  Scenario: 4. Unregister from production
       Then "all" host is unsubscribed and unregistered
        and subscription status is unknown on "all"

  Scenario: 5. Subscribe to stage
      When "all" host is auto-subscribed to "stage"
       Then subscription status is ok on "all"
        and "1" entitlement is consumed on "all"

  Scenario: 6. Gather initial RPM list
       When "initial" RPM list is collected
       Then the text file with the "initial" RPM list is retrieved

  Scenario: 7. 'atomic host upgrade' is successful
      Given there is "2" atomic host tree deployed
       When atomic host upgrade is successful
       Then there is "2" atomic host tree deployed

  Scenario: 8. Reboot into the new deployment
      Given there is "2" atomic host tree deployed
        and the original atomic version has been recorded
       When wait "30" seconds for "all" to reboot
       Then the current atomic version should not match the original atomic version

  Scenario: 9. Gather upgraded RPM list
       When "upgraded" RPM list is collected
       Then the text file with the "upgraded" RPM list is retrieved

  Scenario: 10. Collect the data about the upgraded system
      Given the data collection script is present
       When the data collection script is run
       Then the generated data files are retrieved

  Scenario: 11. Rollback to the original deployment
      Given there is "2" atomic host tree deployed
        and the original atomic version has been recorded
       When atomic host rollback is successful
        and wait "30" seconds for "all" to reboot
       Then the current atomic version should not match the original atomic version

  Scenario: 12. Unregister
       Then "all" host is unsubscribed and unregistered
       and subscription status is unknown on "all"


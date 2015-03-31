Feature: Atomic host sanity test for new upgrade tree
    Describes tests for upgrade/rollback to/from new ostree

Background: Atomic hosts are discovered
      Given "all" hosts from dynamic inventory
        and "all" host

  Scenario: 1. Host provisioned and subscribed
       When "all" host is auto-subscribed to "stage"
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

  Scenario: 4. Collect the data about the upgraded system
      Given the data collection script is present
       When the data collection script is run
       Then the data collection output file is present
        and the data collection output files are retrieved

  Scenario: 5. Rollback to the original deployment
      Given there is "2" atomic host tree deployed
        and the original atomic version has been recorded
       When atomic host rollback is successful
        and wait "30" seconds for "all" to reboot
       Then the current atomic version should not match the original atomic version

  Scenario: 6. Unregister
       Then "all" host is unsubscribed and unregistered
        and subscription status is unknown on "all"

Feature: Atomic host sanity test for new QCOW images
    Describes the basic 'atomic host' command functionality for a fresh
    QCOW image install.

Background: Atomic hosts are discovered
      Given "all" hosts from dynamic inventory
        and "all" host

  Scenario: 1. Host unprovisioned and 'atomic host upgrade' is used
      Given the original atomic version has been recorded
       Then atomic host upgrade should return an unregistered error
        and current atomic version should match the original atomic version

  Scenario: 2. Host unprovisioned and 'atomic host rollback' is used
      Given there is "1" atomic host tree deployed
       Then atomic host rollback should return a deployment error
        and there is "1" atomic host tree deployed

  Scenario: 3. Host provisioned and subscribed
       When "all" host is auto-subscribed to "stage"
       Then subscription status is ok on "all"
        and "1" entitlement is consumed on "all"

  Scenario: 4. 'atomic host upgrade' is successful when no upgrade available
      Given there is "1" atomic host tree deployed
       Then atomic host upgrade reports no upgrade available
        and there is "1" atomic host tree deployed

  Scenario: 5. 'atomic host rollback' reports error about single deployment
      Given there is "1" atomic host tree deployed
       Then atomic host rollback should return a deployment error
        and there is "1" atomic host tree deployed

  Scenario: 6. Unregister
       Then "all" host is unsubscribed and unregistered
        and subscription status is unknown on "all"

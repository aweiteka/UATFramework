Feature: Atomic host sanity test for new QCOW images
    Describes the basic 'atomic host' command functionality for a fresh
    QCOW image install.

Background: Atomic hosts are discovered
      Given "all" hosts from dynamic inventory
        and "all" host

  Scenario: 1. Host unprovisioned and 'atomic host upgrade' is used
      Given active tree version is at "7.1.0" on "all"
       Then atomic host upgrade should return an unregistered error
        and active tree version is at "7.1.0" on "all"

  Scenario: 2. Host unprovisioned and 'atomic host rollback' is used
      Given there is "1" atomic host tree deployment
       Then atomic host rollback should return a deployment error
        and there is "1" atomic host tree deployment

  Scenario: 3. Host provisioned and subscribed
       When "all" host is auto-subscribed to "stage"
       Then subscription status is ok on "all"
        and "1" entitlement is consumed on "all"

  Scenario: 4. 'atomic host upgrade' is successful when no upgrade available
      Given there is "1" atomic host tree deployment
       Then atomic host upgrade reports no upgrade available
        and there is "1" atomic host tree deployment

  Scenario: 5. 'atomic host rollback' reports error about single deployment
      Given there is "1" atomic host tree deployment
       Then atomic host rollback should return a deployment error
        and there is "1" atomic host tree deployment

  Scenario: 6. Unregister
       Then "all" host is unsubscribed and unregistered
        and subscription status is unknown on "all"

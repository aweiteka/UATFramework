Feature: ostree host smoke test
    Describes the basic atomic upgrade/rollback functionality

Background: Atomic hosts are discovered
      Given "all" hosts from dynamic inventory

  Scenario: 1. Host unprovisioned and 'atomic host upgrade' is used
      Given "all" host
      Given active tree version is at "7.1.0" on "all"
       When atomic "host upgrade" is run on "all"
       Then the error message should indicate the system is unregistered
        and active tree version is at "7.1.0" on "all"

  Scenario: 1. Host provisioned and subscribed
      Given "all" host
       When "all" host is auto-subscribed to "stage"
       Then subscription status is ok on "all"
        and "1" entitlement is consumed on "all"

  Scenario: 2. Unregister
       Then "all" host is unsubscribed and unregistered
        and subscription status is unknown on "all"

Feature: ostree host smoke test
    Describes the basic atomic upgrade/rollback functionality

Background: Atomic hosts are discovered
      Given "all" hosts from dynamic inventory

  Scenario: 1. Host unprovisioned and 'atomic host upgrade' is used
      Given "all" host
        and active tree version is at "7.1.0" on "all"
       Then atomic host upgrade should return an unregistered error
        and active tree version is at "7.1.0" on "all"

  Scenario: Y. Host provisioned and subscribed
      Given "all" host
       When "all" host is auto-subscribed to "stage"
       Then subscription status is ok on "all"
        and "1" entitlement is consumed on "all"

  Scenario: Z. Unregister
       Then "all" host is unsubscribed and unregistered
        and subscription status is unknown on "all"

Feature: ostree host smoke test
    Describes the basic atomic upgrade/rollback functionality

Background: Atomic hosts are discovered
      Given "all" hosts from dynamic inventory

  Scenario: 1. Host provisioned and subscribed
      Given "all" host
       When "all" host is auto-subscribed to "stage"
       Then subscription status is ok on "all"
        and "1" entitlement is consumed on "all"

  Scenario: 2. Unregister
       Then "all" host is unsubscribed and unregistered

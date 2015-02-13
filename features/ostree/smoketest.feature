Feature: ostree host smoke test
    Describes the basic atomic upgrade/rollback functionality

Background: Atomic hosts are discovered
      Given "all" hosts from dynamic inventory

  Scenario: 1. Host provisioned and subscribed
      Given "all" host
       When "all" host is auto-subscribed
       Then subscription status is ok on "all"
        and "1" entitlement is consumed on "all"

  Scenario: 2. Upgrade ostree
      Given active tree version is at "7.0.0" on "all"
       When atomic "upgrade" is run on "all"
       Then wait "60" seconds for "all" to reboot
       Then active tree version is at "7.0.1" on "all"

  Scenario: 3. Rollback ostree
      Given active tree version is at "7.0.1" on "all"
       When atomic "rollback" is run on "all"
       Then wait "60" seconds for "all" to reboot
       Then active tree version is at "7.0.0" on "all"

  Scenario: 4. Unregister
       Then "all" host is unsubscribed and unregistered

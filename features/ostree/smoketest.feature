Feature: ostree host smoke test
    Describes the basic atomic upgrade/rollback functionality

Background: Atomic hosts are discovered
      Given "cihosts" hosts from dynamic inventory

  Scenario: 1. Host provisioned and subscribed
      Given "cihosts" host
       When "cihosts" host is auto-subscribed
       Then subscription status is ok on "cihosts"
        and "1" entitlement is consumed on "cihosts"

  Scenario: 2. Upgrade ostree
      Given active tree version is at "7.0.0" on "cihosts"
       When atomic "upgrade" is run on "cihosts"
       Then wait "60" seconds for "cihosts" to reboot
       Then active tree version is at "7.0.1" on "cihosts"

  Scenario: 3. Rollback ostree
      Given active tree version is at "7.0.1" on "cihosts"
       When atomic "rollback" is run on "cihosts"
       Then wait "60" seconds for "cihosts" to reboot
       Then active tree version is at "7.0.0" on "cihosts"

  Scenario: 4. Unregister
       Then "cihosts" host is unsubscribed and unregistered

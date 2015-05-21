Feature: Atomic cloud-init subscription-manager plugin test (bad pool-id)
    Tests whether subscription-manager fails to attach non-existent pool-id

Background: Atomic hosts are discovered
      Given "all" hosts from dynamic inventory
        and "all" host

  Scenario: 0. subscription-manager plugin has failed
       Given cloud-init on "all" host is running
       Then wait for rh_subscription_manager plugin to finish
        and check if it failed

  Scenario: 1. subscription-manager fails to attach non-existent pool-id
       Given cloud-init on "all" host is running
       Then check if the subscription-manager failed to attach non-existent pool-id

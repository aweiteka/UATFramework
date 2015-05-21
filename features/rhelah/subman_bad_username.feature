Feature: Atomic cloud-init subscription-manager plugin test (bad username)
    Tests whether subscription-manager fails to register when provided with bad username

Background: Atomic hosts are discovered
      Given "all" hosts from dynamic inventory
        and "all" host

  Scenario: 0. subscription-manager plugin has failed
       Given cloud-init on "all" host is running
       Then wait for rh_subscription_manager plugin to finish
        and check if it failed

  Scenario: 1. subscription-manager fails to register with bad username
       Given cloud-init on "all" host is running
       Then check if the subscription-manager failed to register with bad username

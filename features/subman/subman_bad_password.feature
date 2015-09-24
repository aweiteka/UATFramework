Feature: Atomic cloud-init subscription-manager plugin test (bad password)
    Tests whether subscription-manager fails to register when provided with bad password

Background: Atomic hosts are discovered
      Given "all" host

  Scenario: 0. subscription-manager plugin has failed
       Given cloud-init on "all" host is running
       Then wait for rh_subscription_manager plugin to finish
        and check if the rh_subscription_manager failed to complete

  Scenario: 1. subscription-manager fails to register with bad password
       Given cloud-init on "all" host is running
       Then check if the subscription-manager failed to register with bad password

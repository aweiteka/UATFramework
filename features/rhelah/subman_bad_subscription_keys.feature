Feature: Atomic cloud-init subscription-manager plugin test (bad subscription keys)
    Tests whether subscription-manager fails to complete when incorrect subscription keys are provided

Background: Atomic hosts are discovered
      Given "all" hosts from dynamic inventory
        and "all" host

  Scenario: 0. subscription-manager plugin has failed
       Given cloud-init on "all" host is running
       Then wait for rh_subscription_manager plugin to finish
        and check if the rh_subscription_manager failed to complete

  Scenario: 1. subscription-manager fails to complete when incorrect subscription keys are provided
       Given cloud-init on "all" host is running
       Then check if the subscription-manager issued error message when incorrect subscription keys are provided

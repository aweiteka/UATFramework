Feature: Atomic cloud-init subscription-manager plugin test (non-existent repo)
    Tests whether subscription-manager doesn't crash when trying to add non-existent repo

Background: Atomic hosts are discovered
      Given "all" hosts from dynamic inventory
        and "all" host

  Scenario: 0. subscription-manager plugin has been run successfully
       Given cloud-init on "all" host is running
       Then wait for rh_subscription_manager plugin to finish
        and check if the rh_subscription_manager completed successfully

  Scenario: 1. subscription-manager plugin doesn't crash when trying to add non-existent repo
       Given cloud-init on "all" host is running
       Then check if an error message is shown in the log when trying to add non-existent repo

Feature: Atomic cloud-init subscription-manager plugin test
    Tests whether subscription-manager uses provided credentials to register to the CDN, attaches pools, enables/disables provided repoids

Background: Atomic hosts are discovered
      Given "all" hosts from dynamic inventory
        and "all" host

  Scenario: 0. subscription-manager plugin has been run successfully
       Given cloud-init on "all" host is running
       Then wait for rh_subscription_manager plugin to finish
        and check if it completed successfully

  Scenario: 1. subscription-manager registers successfully
       Given cloud-init on "all" host is running
       Then check if the subscription-manager successfully registered

  Scenario: 2. subscription-manager plugin attaches existing pools
       Given cloud-init on "all" host is running
       Then check if it successfully attached defined pools

  Scenario: 3. subscription-manager plugin enables existing listed repoids
       Given cloud-init on "all" host is running
       Then check if the existing listed repoids were enabled

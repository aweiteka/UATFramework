Feature: Atomic cloud-init subscription-manager plugin test (mixed pool-id)
    Tests whether subscription-manager completes successfully when provided mix of existent and non-existent pools

Background: Atomic hosts are discovered
      Given "all" hosts from dynamic inventory
        and "all" host

  Scenario: 0. subscription-manager plugin has been run successfully
       Given cloud-init on "all" host is running
       Then wait for rh_subscription_manager plugin to finish
        and check if the rh_subscription_manager completed successfully

  Scenario: 1. subscription-manager fails to attach non-existent pool-id and attaches existent pool-id
       Given cloud-init on "all" host is running
       Then check if the subscription-manager failed to attach non-existent pool-id
	   and check if subscription-manager successfully attached existing pools

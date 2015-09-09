Feature: Atomic cloud-init subscription-manager plugin test (re-enable/re-disable repos)
    Tests whether subscription-manager successfully finishes when attempting to enable/disable already enabled/disabled repos and issues informational message

Background: Atomic hosts are discovered
      Given "all" hosts from dynamic inventory
        and "all" host

  Scenario: 0. subscription-manager plugin has been run successfully
       Given cloud-init on "all" host is running
       Then wait for rh_subscription_manager plugin to finish
        and check if the rh_subscription_manager completed successfully

  Scenario: 1. subscription-manager registers successfully
       Given cloud-init on "all" host is running
       Then check if the subscription-manager successfully registered

  Scenario: 2. subscription-manager plugin attaches existing pools
       Given cloud-init on "all" host is running
       Then check if subscription-manager successfully attached existing pools

  Scenario: 3. subscription-manager plugin issues informational message about already enabled/disabled repos
       Given cloud-init on "all" host is running
       Then check the Repo "rhel-rs-for-rhel-7-server-eus-rpms" is already enabled message appearance
		and check the Repo "rh-gluster-3-splunk-for-rhel-7-server-rpms" not disabled because it is not enabled message appearance

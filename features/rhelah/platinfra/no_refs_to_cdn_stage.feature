Feature: Verify that there are no references to the Stage environment on Atomic Host after upgrade to the latest ostree

Background: Atomic hosts are discovered
      Given "all" host

Scenario: 0. register to the stage environment, upgrade to the latest OSTree version, reboot and check whether there are no references to the Stage environment
       When "all" host is auto-subscribed to "prod"
		and atomic host upgrade is successful
		and wait "30" seconds for "all" to reboot
       Then check whether there are no references to the "cdn.stage.redhat.com"

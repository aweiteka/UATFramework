@host_subscribed @ah_upgrade @services_status
Feature:  Verify service can works well on host
          Check one or more service works well with default cfg in host

Background: Atomic hosts are discovered
      Given "all" hosts can be pinged

  Scenario: 1. Check service status
        And "stop" "running" services

  Scenario: 2. Start service
      Given "start" "all" services
       Then services status is "running"

  Scenario: 3. Stop service
      Given "stop" "all" services
       Then services status is "dead"

  Scenario: 4. Restart service
      Given "start" "all" services
       When services status is "running"
       Then "restart" "all" services
        And services status is "running"

  Scenario: 5. Enable services
      Given "enable" "all" services
       When wait "30" seconds for "all" to reboot
       Then services status is "running"

  Scenario: 6. Disable service
      Given "disable" "all" services
        And "stop" "all" services
       When services status is "dead"
        And wait "30" seconds for "all" to reboot
        And services status is "dead"

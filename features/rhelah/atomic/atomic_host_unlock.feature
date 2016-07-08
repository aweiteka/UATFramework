@atomic @host_subscribed @ah_upgrade
Feature: Atomic host unlock sanity test
    Describes the basic 'atomic host unlock' command test

Background: Atomic hosts are discovered
      Given "all" hosts can be pinged

  @change_to_development_mode
  Scenario: 1. change atomic host to development mode
      When switch atomic host to development mode
      When create file "/usr/unlock_dev_test"
      Then check unlock status "Unlocked: development" exists
       and Check whether mount option "overlay /usr overlay rw" exists
       and run command "shell ls /usr/unlock_dev_test"

  @reboot_host_then_check_dev_mode
  Scenario: 2. reboot atomic host then check development mode
      When wait "60" seconds for "all" to reboot
      Then check unlock status "Unlocked: development" does not exists "true"
       and check whether mount option "overlay /usr overlay rw" does not exist
       and run command "shell ls /usr/unlock_test" ignore error "true"

  @change_to_hotfix_mode
  Scenario: 3. change atomic host to hotfix mode
      When switch atomic host to "hotfix" mode
      When create file "/usr/unlock_hotfix_test"
      Then check unlock status "Unlocked: hotfix" exists
       and Check whether mount option "overlay /usr overlay rw" exists
       and run command "shell ls /usr/unlock_hotfix_test"

  @reboot_host_then_check_hotfix_mode
  Scenario: 4. reboot atomic host then check hotfix mode
      When wait "60" seconds for "all" to reboot
      Then check unlock status "Unlocked: hotfix" exists
       and check whether mount option "overlay /usr overlay rw" exists
       and run command "shell ls /usr/unlock_hotfix_test"

  @rollback_host_after_hotfix_mode
  Scenario: 5. Rollback to the original deployment
      When atomic host rollback is successful
       and wait "60" seconds for "all" to reboot
      Then check whether mount option "overlay /usr overlay rw" does not exist
       and run command "shell ls /usr/unlock_test" ignore error "true"

  @rollback_host_to_hotfix_mode
  Scenario: 6. Rollback to the hotfix deployment
      When atomic host rollback is successful
       and wait "60" seconds for "all" to reboot
      Then check unlock status "Unlocked: hotfix" exists
       and Check whether mount option "overlay /usr overlay rw" exists
       and run command "shell ls /usr/unlock_hotfix_test"

  @rollback_host
    Scenario: 7. Rollback to the original deployment
      When atomic host rollback is successful
       and wait "60" seconds for "all" to reboot
      Then check whether mount option "overlay /usr overlay rw" does not exist
       and run command "shell ls /usr/unlock_test" ignore error "true"

Feature: Atomic host sanity test for new QCOW images
    Describes the basic 'atomic host' command functionality for a fresh
    QCOW image install.

Background: Atomic hosts are discovered
      Given "all" hosts from static inventory
        and "all" host

  Scenario: 3. Host provisioned and subscribed
       When "all" host is auto-subscribed to "stage"
       Then subscription status is ok on "all"
        and "1" entitlement is consumed on "all"

  Scenario: 4. 'atomic host upgrade' is successful
      Given there is "1" atomic host tree deployed
       When atomic host upgrade is successful
       Then there is "2" atomic host tree deployed

  Scenario: 5. Reboot into the new deployment
     Given: there is "2" atomic host tree deployed
        and the original atomic version has been recorded
      Then: wait "20" seconds for "all" to reboot


  Scenario: 6. Unregister
       Then "all" host is unsubscribed and unregistered
        and subscription status is unknown on "all"

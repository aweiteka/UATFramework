Feature: Satellite6 API Example

  Scenario: Create an organizaion
    Given "satellite" host
      and run command "fetch src=/root/cobbler.ks dest=/tmp/" on "satellite"
     When organization "testorg" is created
      and run command "stat path=/" on "satellite"
     Then there are "3" organizations

  Scenario: Delete an organization
    Given "satellite" host
     When organization "testorg" is deleted
     Then there are "2" organizations

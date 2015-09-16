@docker
Feature: Docker pull
  Run 'docker pull' on list of images

  Scenario Outline: docker pull
      Given "all" hosts from dynamic inventory
       When docker pull "<image>:<tag>"
       Then remove docker image "<image>:<tag>"

  Examples: docker images
    | image         | tag    |
    | rhel7         | latest |
    | rhel7         | 0      |
    | rhel7         | 0-21   |
    | rhel7         | 0-23   |
    | rhel7         | 1      |
    | rhel7         | 1-3    |
    | rhel6         | latest |
    | rhel6         | 5      |
    | rhel6         | 5-11   |
    | rhel6         | 5-12   |
    | redhat/rhel7  | latest |
    | redhat/rhel7  | 0      |
    | redhat/rhel7  | 0-21   |
    | redhat/rhel7  | 0-23   |
    | redhat/rhel7  | 1      |
    | redhat/rhel7  | 1-3    |
    | redhat/rhel6  | latest |
    | redhat/rhel6  | 5      |
    | redhat/rhel6  | 5-11   |
    | redhat/rhel6  | 5-12   |

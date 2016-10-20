@host_subscribed
Feature: tests whether RH CA pinning works for rpm-ostree
    It is critical for security that we're "pinned" to the RHN CA cert. If another server certificate is presented we should error out with something like Unacceptable TLS certificate.

Scenario: Running through a proxy should give a TLS error
    Given "git" is already installed on "rhel7"
    When checkout the git repo "https://github.com/ljozsa/tools.git" on "rhel7"
    And run command "command /root/tools/mitmproxy_install.sh" on "rhel7"
    Then atomic host upgrade on "rhelah" using the proxy on "rhel7" should fail

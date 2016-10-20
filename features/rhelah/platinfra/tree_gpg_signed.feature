Feature: Check if the current tree is signed with Red Hat's release key 2

Background: Atomic hosts are discovered
      Given "all" host

  Scenario: 0. import Red Hat's release key 2 and verify it's public fingerprint 
       When import Red Hat's release key 2 to the superuser's keyring succeeds
       Then verify if Red Hat's release key 2 matches public fingerprint

  Scenario: 1. download gpgverify.py script check its sha256sum and use it to verify OSTree signature when using OSTree < 7.1.2
       When download "https://raw.githubusercontent.com/cgwalters/ostree-scripts/d40198793ac3d9809ca7c215e2aaef239b23194e/ostree-script-gpgverify" script with sha256sum "efa9a28f28dd5bdc26470e996d5898827fd0fb227ecd460e8c817be893af913f" finishes
		and OSTree version is lower than "7.1.2"
       Then use the gpgverify.py script to verify gpg signatures

  Scenario: 2. register to the stage environment, upgrade to the latest OSTree version, reboot and verify whether is it signed with the Red Hat's release key 2 using ostree status
       When "all" host is auto-subscribed to "stage"
		and atomic host upgrade is successful
		and wait "30" seconds for "all" to reboot
       Then use ostree show command to verify gpg signatures

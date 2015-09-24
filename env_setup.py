"""
Functions for environment preparition and cleanup.
"""


import behave


def host_subscribed_prepare(context):
    context.execute_steps(u"""
        When "{hosts}" host is auto-subscribed to "{server}"
        Then subscription status is ok on "{hosts}"
         And "1" entitlement is consumed on "{hosts}"
        """.format(hosts=context.hosts,
                   server=context.subman_server))
    print("Register %s hosts to %s" % (context.hosts, context.subman_server))


def host_subscribed_cleanup(context):
    context.execute_steps(u"""
        Then "{hosts}" host is unsubscribed And unregistered
         And subscription status is unknown on "all"
        """.format(hosts=context.hosts))
    print("Unregister %s hosts" % context.hosts)


def ah_upgrade_prepare(context):
    context.execute_steps(u"""
        Given get the number of atomic host tree deployed
         When confirm atomic host tree to old version
          And atomic host upgrade is successful
         Then wait "60" seconds for "all" to reboot
          And there is "2" atomic host tree deployed
        """)


def ah_upgrade_no_reboot_prepare(context):
    context.execute_steps(u"""
        Given get the number of atomic host tree deployed
         When confirm atomic host tree to old version
          And atomic host upgrade is successful
          And there is "2" atomic host tree deployed
        """)

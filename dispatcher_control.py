#!/usr/bin/env python
# coding=utf-8
import xmlrpclib
import sys
"""
Insert Asterisk Node into Kamailio dispatcher. Work In Progress...
"""
__author__ = 'JustinZimmer'




def arguments():
    if not len(argv[1:]) == 3:
        print "Incorrect arguments.\n\nUsage:\n\t{0} ACTION KAMBOX ASTHOST\n".format(path.basename(__file__))
        exit(1)
    else:
        return argv[1:]

def dispatcher():
    action, kamBox, astHost = arguments()

    if action == 'add':
        ...
    elif action == 'remove':
        ...
    else:
        print "Invalid Action: {0]".format(action)
        sys.exit(1)

# Reload Dispatcher List.

servURL = 'http://{0}:5060'.format(kamBox)

server = xmlrpclib.ServerProxy(servURL)
res = getattr(server, 'dispatcher.reload')
print res

# This should be a server that runs on Kam server and runs kamctl to
# prevent updating DB externally... ??

#!/usr/bin/env python
# coding=utf-8
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import logging
import socket
from subprocess import call

"""
Simple RPC Server to wait for node check in on Kamailio.
"""
__author__ = 'JustinZimmer'

logging.basicConfig(level=logging.DEBUG)


class RPCServer(SimpleXMLRPCServer):

    quit = False

    def __init__(self, *args, **kwargs):
        self._timedout = False
        self.status = 'INIT'
        SimpleXMLRPCServer.__init__(self, *args, **kwargs)

    def handle_request(self):
        self._timedout = False
        self.status = "WAITING"
        return SimpleXMLRPCServer.handle_request(self)

    def handle_timeout(self):
        self.status = 'TIMEDOUT'
        self._timedout = True
        return self.status

    def serve_forever(self):
        self.quit = False
        while not self.quit:
            self.handle_request()

    def shutdown(self):
        self.quit = True
        return 1

    def timedout(self):
        return self._timedout


def KamCheckIn(host):
    logging.debug('Adding Host: %s', host)
    if hostname_resolves(host):
        cmd = "kamctl dispatcher add 2 sip:{0} 0 0 '' '{0}'".format(host)
        cmdReload = "kamctl dispatcher reload"
        retCode = call(cmd, shell=True)
        retCode = call(cmdReload, shell=True)
        return retCode
    else:
        return False
    # print status
    # return status


def KamCheckOut(host):
    logging.debug('Removing Host: %s', host)
    cmd = "kamctl db exec \"delete from dispatcher "
    "where description ='{0}';\"".format(host)
    cmdReload = "kamctl dispatcher reload"
    retCode = call(cmd, shell=True)
    retCode = call(cmdReload, shell=True)
    return retCode
    # print status
    # return status


def Shutdown():
    logging.debug('Shutting down...')
    server.shutdown()


def hostname_resolves(hostname):
    try:
        socket.gethostbyname(hostname)
        return True
    except socket.error:
        return False

server = RPCServer(('0.0.0.0', 8787),
                   SimpleXMLRPCRequestHandler,
                   logRequests=False,
                   allow_none=True)
# server.timeout=15 # seconds


server.register_function(KamCheckIn, 'check_in')
server.register_function(KamCheckOut, 'check_out')
server.register_function(Shutdown, 'shutdown')


try:
    server.serve_forever()
    # print '{0} just happened!'.format(server.status)
    # print server.status
except Exception, e:
    logging.debug('Unexpected Exception: %s', str(e))
    # server.status="EXCEPTION: {0}".format(str(e))
    # print server.status
except KeyboardInterrupt:
    logging.debug("User Aborted!")

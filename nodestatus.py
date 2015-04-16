#!/usr/bin/env python
# coding=utf-8
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
import logging
import socket
import os
# from subprocess import call
from subprocess import check_output
from linux_metrics import cpu_stat
from linux_metrics import mem_stat

"""
Simple RPC Server to respond to status requests and node commands.
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


def serviceStatus(service):

    svcStatus = False
    if service == "Asterisk":
        print "Checking Asterisk..."
        try:
            asterisk = check_output("service asterisk status", shell=True)
            print asterisk
            if asterisk.find("is running") != -1:
                svcStatus = True
            else:
                svcStatus = False
        except:
            svcStatus = False

    elif service == "Jboss":
        startString = "JBoss (MX MicroKernel) [4.2.2.GA "
        "(build: SVNTag=JBoss_4_2_2_GA date=200710221139)] Started in "
        logfile = "/var/log/weblog"
        svcStatus = False
        try:
            log = open(logfile, 'r')
            # read = mmap.mmap(log.fileno(), 0, access=mmap.ACCESS_READ)
            lines = log.readlines()

            for elem in lines:
                if elem.find(startString) != -1:
                    svcStatus = True
        except:
            print "Couldn't open LogFile!"

    else:
        print "Unrecognized Service: {0}".format(service)

    return svcStatus

def callCount():
    print "Checking Call Count..."
    callCount = 0
    try:
        asterisk = check_output('asterisk -rx "core show channels"', shell=True)
        #print asterisk
        if asterisk.find("command not found") != -1:
            callCount = -1
        else:
            lines = asterisk.readlines()

            for elem in lines:
                if elem.find("active calls") != -1:
                    callCount = int(elem.split()[0])
            
    except:
        callCount = -1

    return callCount

def listChannels():
    print "Checking Call Count..."
    channelList = {}
    try:
        asterisk = check_output('asterisk -rx "core show channels concise"', shell=True)
        #print asterisk
        if asterisk.find("command not found") != -1:
            channelList = False
        else:
            lines = asterisk.readlines()

            for elem in lines:
                if elem.find("Bridge") != -1:
                    callCount = int(elem.split()[0])
    except:
        callCount = -1

    return callCount

def upTime():
    print "Checking Up Time..."
    load = 0
    try:
        upString = check_output('uptime', shell=True)
        #print asterisk
        loadIndex = upString.find("load average: ")
        loadList = upString[loadIndex+14:].strip().split(', ')
        load = float(loadList[0])
    except:
        load = -1

    return load

def serverStats():
    cpuPercents = cpu_stat.cpu_percents(1)
    statDict = {}
    statDict["ioWait"] = cpuPercents['iowait']
    statDict["system"] = cpuPercents['system']
    statDict["idle"] = cpuPercents['idle']
    statDict["user"] = cpuPercents['user']
    statDict["cpuUsed"] = round(100 - cpuPercents['idle'])
    statDict["loadAvg"] = cpu_stat.load_avg()
    statDict["memUsed"], statDict["memTot"], _, _, _, _ = mem_stat.mem_stats()
    statDict["memFree"] = memTot-memUsed
    return statDict



def Shutdown():
    logging.debug('Shutting down...')
    server.shutdown()


def hostname_resolves(hostname):
    try:
        socket.gethostbyname(hostname)
        return True
    except socket.error:
        return False

pid = os.getpid()
op = open("/var/run/nodestatus.pid", "w")
op.write("%s" % pid)
op.close()

server = RPCServer(('0.0.0.0', 8787),
                   SimpleXMLRPCRequestHandler,
                   logRequests=False,
                   allow_none=True)
# server.timeout=15 # seconds


server.register_function(serviceStatus, 'checkService')
server.register_function(Shutdown, 'shutdown')
server.register_function(serverStats, 'serverStats')
server.register_function(callCount, 'callCount')


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

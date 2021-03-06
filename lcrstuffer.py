#!/usr/bin/env python
# coding=utf-8
import MySQLdb
import ast
import json
from sys import argv
from os import path
from os import stat
"""
Insert Asterisk Node into Kamailio dispatcher.
"""
__author__ = 'JustinZimmer'


def arguments():
    if len(argv[1:]) < 2 or len(argv[1:]) > 3:
        print "Incorrect arguments.\n\nUsage:"
        "\n\t{0} NUMBERFILE ACTION (CONFIG)\n".format(path.basename(__file__))
        exit(1)
    elif len(argv[1:]) == 2:
        arguments = [argv[1], argv[2], 'cfgDict.json']
        print arguments
        return arguments
    else:
        arguments = [argv[1], argv[2], argv[3]]
        print arguments
        return arguments


def lcrImport():
    numberFile, action, configfile = arguments()
    if not path.exists(numberFile) or stat(numberFile).st_size == 0:
        print """Specified file does not exist or is empty,
please check filename and try again!"""
        exit(1)
    cfgDict = {}
    if path.exists(configfile):
        try:
            cfgDict = json.load(open(configfile))
        except:
            print "{0} is invalid!\n".format(configfile)
            exit(1)
    else:
        makeNew = raw_input("""You are missing the necessary parameter file: {0}.\n
            Would you like to create a new one and manually enter parameters?
            (Y/N): """.format(configfile))
        if makeNew.strip()[0:1].upper() == 'Y':
            cfgDict = cfgParams(configfile)
        else:
            print "Oh well, I tried..."
            exit(1)
    try:
        db = MySQLdb.connect(host=cfgDict['host'], user=cfgDict['user'],
                             passwd=cfgDict['passwd'], db=cfgDict['db'])
    except:
        print """I'm sorry, I couldn't connect to your database,
             please check your parameters and try again, buh-bye!"""
        exit(1)

    print db
    c = db.cursor()
    print c

    with open(numberFile) as f:
        for line in f:
            number = line.strip()
            if not number:
                print "Line is empty... what gives? Skipping..."
                continue
            print "Figuring out what to do with {0}...".format(number)
            if action.lower() == 'import':
                print "Importing {0}".format(number)
                exists = c.execute("""SELECT id FROM lcr_rule
                                 WHERE prefix=%s""", [number])
                if exists > 0:
                    print """{0} already exists in the lcr_rule table.
Skipping to prevent duplicate routes.""".format(number)
                    continue
                c.execute("""INSERT INTO lcr_rule (lcr_id, prefix, stopper, enabled)
                         VALUES (1,%s,1,1)""", [number])
                c.execute("SELECT id FROM lcr_rule WHERE prefix=%s", [number])
                result = c.fetchone()
                if result is None:
                    print "Something went wrong!!! Result Empty! ABORT! ABORT!"
                    c.close()
                    db.close()
                    exit(1)

                print "Result: {0}".format(result[0])
                ruleID = int(result[0])
                for gw in cfgDict['gwList']:
                    print """Inserting Rule Target for {0} to GW: {1}""".format(number, gw)
                    c.execute("""INSERT INTO lcr_rule_target (lcr_id, rule_id, gw_id, priority, weight)
                        VALUES (1,%s,%s,0,1)""", [int(ruleID), int(gw)])
                print "{0} has been imported.".format(number)

            elif action.lower() == 'remove':
                r = c.execute("""DELETE FROM lcr_rule_target WHERE rule_id IN (
                    SELECT id FROM lcr_rule WHERE prefix=%s)""", [number])
                if r > 0:
                    print "{0} rule target(s) deleted for {1}.".format(
                        r, number)
                else:
                    print "There were no rule targets for {0}".format(number)

                r = c.execute("DELETE FROM lcr_rule WHERE prefix=%s", [number])
                if r > 0:
                    print "{0} rule(s) deleted for {1}.".format(r, number)
                else:
                    print "There were no rules for {0}".format(number)

                print "{0} has been removed.".format(number)
            elif action.lower() == 'enable':
                ruleState(number, 1, 'en', c)
            elif action.lower() == 'disable':
                ruleState(number, 0, 'dis', c)
            elif action.lower() == 'test':
                print "TEST!!! - Config File: {0}, Number: {1}, GW List: {2}".format(number, configfile, cfgDict['gwList'])
            else:
                print """You did not specify a valid action for this list.\n
                    Valid actions are: import, remove, enable, disable."""
                c.close()
                exit(1)
        db.commit()
        c.close()
        db.close()
        print "Action: {0} for file: {1} has been completed!".format(
            action, numberFile)


def ruleState(number, state, prefix, cursor):
    r = cursor.execute("""UPDATE lcr_rule SET enabled=%s
                WHERE prefix=%s""", [state, number])
    if r > 0:
        print "{0} rule(s) {1}abled for {2}.".format(r, prefix, number)
    else:
        r = cursor.execute("SELECT id FROM lcr_rule WHERE prefix=%s", [number])
        if r > 0:
            print "Rule for {0} was already {1}abled.".format(number, prefix)
        else:
            print "Rule for {0} does not exist, nothing to do.".format(number)
    return 1


def cfgParams(filename):
    cfgDict = {}
    cfgDict['host'] = raw_input('Enter your kamailio DB host: ')
    cfgDict['user'] = raw_input('Enter your kamailio DB user: ')
    cfgDict['passwd'] = raw_input('Enter your kamailio DB password: ')
    cfgDict['db'] = raw_input('Enter your kamailio DB name: ')
    strGWList = raw_input('Enter your LCR GW ID list (comma seperated): ')
    cfgDict['gwList'] = ast.literal_eval("({0})".format(strGWList))
    json.dump(cfgDict, open(filename, 'w'))
    return cfgDict

lcrImport()

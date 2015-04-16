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
    if not len(argv[1:]) == 2:
        print "Incorrect arguments.\n\nUsage:"
        "\n\t{0} NUMBERFILE ACTION\n".format(path.basename(__file__))
        exit(1)
    else:
        return argv[1:]


def lcrImport():
    numberFile, action = arguments()
    if not path.exists(numberFile) or stat(numberFile).st_size == 0:
        print "Specified file does not exist or is empty, please check filename and try again!"
        exit(1)
    cfgDict = {}
    if path.exists('cfgDict.json'):
        try:
            cfgDict = json.load(open('cfgDict.json'))
        except:
            print "cfgDict.json is invalid!\n"
            exit(1)
    else:
        makeNew = raw_input("""You are missing the necessary parameter file: cfgdict.json.\n
            Would you like to create a new one and manually enter parameters?
            (Y/N): """)
        if makeNew.strip()[0:1].upper() == 'Y':
            cfgDict = cfgParams()
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
            if action == 'import':
                print "Importing {0}".format(number)
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

            elif action == 'remove':
                c.execute("""DELETE FROM lcr_rule_target WHERE rule_id IN (
                    SELECT id FROM lcr_rule WHERE prefix=%s)""", [number])
                c.execute("DELETE FROM lcr_rule WHERE prefix=%s", [number])
                print "{0} has been removed.".format(number)
            elif action == 'enable':
                c.execute("""UPDATE lcr_rule SET enabled=1
                     WHERE prefix=%s""", [number])
                print "{0} has been enabled.".format(number)
            elif action == 'disable':
                c.execute("""UPDATE lcr_rule SET enabled=0
                     WHERE prefix=%s""", [number])
                print "{0} has been disabled.".format(number)
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


def cfgParams():
    cfgDict = {}
    cfgDict['host'] = raw_input('Enter your kamailio DB host: ')
    cfgDict['user'] = raw_input('Enter your kamailio DB user: ')
    cfgDict['passwd'] = raw_input('Enter your kamailio DB password: ')
    cfgDict['db'] = raw_input('Enter your kamailio DB name: ')
    strGWList = raw_input('Enter your LCR GW ID list (comma seperated): ')
    cfgDict['gwList'] = ast.literal_eval("({0})".format(strGWList))
    json.dump(cfgDict, open('cfgDict.json', 'w'))
    return cfgDict

lcrImport()

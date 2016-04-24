#!/usr/bin/env python3

import os, sys, argparse, signal

# my stuff
from server import server

# TODO: parallel connections

# db access library
import MySQLdb

#irc library
from irc import client

# time libraries
import time
import datetime

import queue
import threading

# regular expresseions
import re

# GLOBAL VARIABLES
_threads = []


def getDB():
     return MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")

def _pull_thread():
    while(True):
        db_pull = getDB()
        cursor_pull = db_pull.cursor()
        pull_result_code = cursor_pull.execute("""SELECT * FROM `IO_Table` WHERE `commandType` = 'NEW_USER';""", ())
        pull_result = cursor_pull.fetchall()
        for result in pull_result:
            print(result)
            data = {
                "userID": result[0],
                "commandType": result[1],
                "argument1": result[2],
                "argument2": result[3],
                "argument3": result[4],
                "timeSent": result[5],
                "processed": bool(result[6]),
                "timeReceived": result[7],
                "fromClient": bool(result[8]),
                "serverID": result[9],
                "channelID": result[10],
                "messageID": result[11]
            }

            if data["commandType"] == "NEW_USER":
                print("NEW USER, FAM")
                message = data["argument1"]
                userID = data["userID"]

                res = cursor_pull.execute("""DELETE FROM `IO_Table` WHERE `messageID` = %s;""", (data["messageID"],)) # delete the message we just processed
                db_pull.commit() # HOWEVER IT ENDS, LET'S JUST DELETE THE MESSAGE

                _threads.append(threading.Thread(target=server.IRCSide, args=(userID,)))
                _threads[-1:][0].start() # start the new user thread (because it was created after the bouncer was already in place)
        print("SLEEP MAIN.PY PULL: 2")
        time.sleep(2)

def start_pull_thread():
    threading.Thread(target=_pull_thread).start()


if __name__ == "__main__":
    aparser = argparse.ArgumentParser()
    aparser.add_argument("--config", "-c", help="Select an alternative config file.")
    args = aparser.parse_args()

    start_pull_thread()

    db = getDB()
    cursor_pull = db.cursor()
    pull_result_code = cursor_pull.execute("""SELECT * FROM `Registered_users`;""")
    pull_result = cursor_pull.fetchall()
    for result in pull_result:
        userID = result[0]
        print("Starting userID: {0}".format(userID))
        _threads.append(threading.Thread(target=server.IRCSide, args=(userID,)))
        _threads[-1:][0].start()

    db.close()
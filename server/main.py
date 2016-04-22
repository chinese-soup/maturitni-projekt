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


def getDB():
     return MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")

def _pull_thread():
    while(True):
        db_pull = getDB()
        cursor_pull = db_pull.cursor()
        pull_result_code = cursor_pull.execute("""SELECT * FROM `IO_Table` WHERE `commandType` = 'NEW_SERVER';""", ())
        pull_result = cursor_pull.fetchall()
        for result in pull_result:
            print(result)
            #(1, 'TEXTBOX', 'AHOJ', '', '', None, 0, None, 1, 2, -1, 73)
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

            if data["commandType"] == "NEW_SERVER":
                message = data["argument1"]
                if message[0] == "/" : # if the first character is a slash the user is trying to exec a command
                    print("Command.")

def start_pull_thread():
    threading.Thread(target=_pull_thread).start()


if __name__ == "__main__":
    aparser = argparse.ArgumentParser()
    aparser.add_argument("--config", "-c", help="Select an alternative config file.")
    aparser.add_argument("userid", help="userid")
    args = aparser.parse_args()
    _threads = []

    if args.userid:
        #irc_side = server.IRCSide(1)

        #irc_side2 = server.IRCSide(2)
        #irc_side.start()
        #irc_side2.start()

        db_pull = getDB()
        cursor_pull = db_pull.cursor()
        pull_result_code = cursor_pull.execute("""SELECT * FROM `IRC_users`;""")
        pull_result = cursor_pull.fetchall()
        for result in pull_result:
            #(1, 'TEXTBOX', 'AHOJ', '', '', None, 0, None, 1, 2, -1, 73)
            data = {
                "userID": result[0]
            }

            _threads.append(threading.Thread(target=server.IRCSide, args=(1,)))
            _threads[-1:].start()

    else:
        print("This should never happen.")

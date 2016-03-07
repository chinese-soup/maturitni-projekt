#!/usr/bin/python3
# coding=utf-8

import os, sys, argparse

# db access lib
import MySQLdb

#irc library
from irc import client

import time
import datetime

import threading # :)))))



"""IRCSide main class"""
class IRCSide(object):
    def __init__(self, _userid):
        super(IRCSide, self).__init__()

        self.client = client.Reactor()
        self.add_handlers()

        self.server_list_instances = list()
        self.server_list_server_objects = list()

        self.load_servers_from_db()

        self.connect_servers()

        self.userID = _userid

        self.db = MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30)
        self.cursor = self.db.cursor()


        self.client.process_forever()


    """Loads user's servers from the database"""
    def load_servers_from_db(self):
        db = MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30)
        cursor = db.cursor()
        userID = 1

        res = cursor.execute("""SELECT * FROM `IRC_servers` WHERE `Registred_users_userID` = %s;""", (userID,))

        result = cursor.fetchall()
        db.close()
        print("RESULT", result)
        servers = list()

        for res in result:
            server_dict_temp = {"serverID": res[0],
                                "serverSessionID": res[1],
                                "nickname": res[2],
                                "isAway": res[3],
                                "isConnected": res[4],
                                "Registred_users_userID": res[5],
                                "serverName": res[6],
                                "serverIP": res[7],
                                "serverPort": res[8],
                                "useSSL": res[9]}
            servers.append(server_dict_temp)
        self.server_list_text = servers

    """
        Adds IRC handlers
    """
    def add_handlers(self):
        self.client.add_global_handler("welcome", self.on_connect)
        self.client.add_global_handler("disconnect", self.on_disconnect)
        self.client.add_global_handler("nicknameinuse", self.on_nicknameinuse)
        self.client.add_global_handler("pubmsg", self.on_pubmsg)
        self.client.add_global_handler("privmsg", self.on_privmsg)
        self.client.add_global_handler("join", self.on_join)
        self.client.add_global_handler("part", self.on_part)
        self.client.add_global_handler("quit", self.on_quit)
        self.client.add_global_handler("nick", self.on_nick)

    """
        Called to connect to a specified server
    """
    def connect_server(self, _serverID, _server, _port, _nickname):
        temp_server_connection_object = self.client.server()

        temp_server_connection_object.serverID = _serverID # důležité: přidává serverID z databáze jako atribut do connection, které se používá při každém global_handleru definovaném o pář řádků výše

        print(temp_server_connection_object.serverID)
        #temp_server_connection_object.setServerID(_serverID)

        self.server_list_server_objects.append(temp_server_connection_object)
        self.server_list_instances.append(temp_server_connection_object.connect(server=_server, port=_port, nickname=_nickname, password=None, username=None, ircname=None))

    """
        Called upon starting the instance
    """
    def connect_servers(self):
        for srvr in self.server_list_text:
            try:
                self.connect_server(srvr["serverID"], srvr["serverIP"], int(srvr["serverPort"]), srvr["nickname"])
            except Exception as exp:
                print("Error occurred.\nWhy: {0}".format(exp)) # TOOD: send errors like these to the client!!!

    """Called: never?"""
    def start(self):
        pass

    """
        Fired when any client successfully connects to an IRC server
    """
    def on_connect(self, connection, event):
        print('[{}] Connected to {}' .format(event.type.upper(), event.source))
        res = self.cursor.execute("""SELECT * FROM `IRC_servers` WHERE `Registred_users_userID` = %s AND `serverID` = %s;""", (self.userID, connection.serverID))
        if res != 0:
            result = self.cursor.fetchall()
            print(result)
            serverID_res = int(result[0][0])
            print("serverID = {}".format(serverID_res))

            if serverID_res == int(connection.serverID): # pokud se získané ID z databáze rovná tomu, které v sobě uchovává connection, redundantní check, ale JTS
                res = self.cursor.execute("""SELECT * FROM `IRC_channels` WHERE `IRC_servers_serverID` = %s;""", (serverID_res,))
                if res != 0:
                    result = self.cursor.fetchall()
                    print("Channels: {}".format(result))

        if client.is_channel("#test.cz"):
            connection.join("#test.cz")

    """Fired when any client is disconnected from an IRC server"""
    def on_disconnect(self, connection, event):
        print('[{}] Disconnected to {}' .format(event.type.upper(), event.source))
        pass

    """Fired when any client receives a message from a channel"""
    def on_pubmsg(self, connection, event):
        print("CONNECTION = {}\n\n".format(connection.__dict__))
        print('[{}] Pubmsg {} {}\n' .format(event.type.upper(), event.source, str(event.__dict__)))
        message = event.arguments[0]

        res = self.cursor.execute("""SELECT * FROM `IRC_servers` WHERE `Registred_users_userID` = %s AND `serverID` = %s;""", (self.userID, connection.serverID))

        if res != 0:
            result = self.cursor.fetchall()
            print(result)
            serverID_res = int(result[0][0])
            print("serverID = {}".format(serverID_res))

            if serverID_res == int(connection.serverID): # pokud se získané ID z databáze rovná tomu, které v sobě uchovává connection, redundantní check, ale JTS
                res = self.cursor.execute("""SELECT * FROM `IRC_channels` WHERE `IRC_servers_serverID` = %s AND `channelName` = %s;""", (serverID_res, event.target))
                if res != 0:
                    result = self.cursor.fetchall()
                    print("Channels: {}".format(result))
                    channelID_res = int(result[0][0])

                    res = self.cursor.execute("""INSERT INTO `IRC_channel_messages` (IRC_channels_channelID,
                    fromHostmask,
                    messageBody,
                    commandType,
                    timeReceived)
                    values (%s, %s, %s, %s, %s)""", (channelID_res, event.source, message, event.type.upper(), datetime.datetime.utcnow()))

                    self.db.commit()

                else:
                    print("WOAH")

            #print("Servers??? {0}".format(result))
            #res2 = self.cursor.execute("""select * from `IRC_channels` where `IRC_servers_serverID` = 1;""", (self.userID,))

        #connection.privmsg(event.target, str(event.__dict__))

    def on_privmsg(self, connection, event):
        print('[{}] Privmsg {}' .format(event.type.upper(), event.source))
        connection.privmsg(event.target, str(event.__dict__))

    def on_join(self, connection, event):
        print('[{}] Join {}' .format(event.type.upper(), event.source))
        connection.privmsg(event.target, str(event.__dict__))

    def on_part(self, connection, event):
        print('[{}] Part {}' .format(event.type.upper(), event.source))


    def on_quit(self, connection, event):
        print('[{}] Quit {}' .format(event.type.upper(), event.source))


    def on_nick(self, connection, event):
        print('[{}] NickChange {}' .format(event.type.upper(), event.source))

    def on_nicknameinuse(self, connection, event):
        print('[{}] NickNameInUse {}' .format(event.type.upper(), event.source))

class WSocket(object):
    """WSocket"""
    def __init__(self, arg):
        super(WSocket, self).__init__()
        self.arg = arg




#!/usr/bin/python3
# coding=utf-8

import os, sys, argparse

# db access lib
import MySQLdb

#irc library
from irc import client

"""IRCSide main class"""
class IRCSide(object):
    def __init__(self, _userid):
        super(IRCSide, self).__init__()

        self.client = client.Reactor()
        self.add_handlers()

        self.server_list_instances = list()

        self.load_servers_from_db()

        self.connect_servers()

        self.client.process_forever()

        self.userID = _userid

        self.db = MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30)
        self.cursor = self.db.cursor()

    """Loads user's servers from the database"""
    def load_servers_from_db(self):
        db = MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30)
        cursor = db.cursor()
        userID = 1

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

    """Adds IRC handlers"""
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


    def connect_server(self, _server, _port, _nickname):
        self.server_list_instances.append(self.client.server().connect(server=_server, port=_port, nickname=_nickname, password=None, username=None, ircname=None))

    def connect_servers(self):
        for srvr in self.server_list_text:
            self.connect_server(srvr["serverIP"], int(srvr["serverPort"]), srvr["nickname"])

    def start(self):
        pass

    def on_connect(self, connection, event):
        print('[{}] Connected to {}' .format(event.type.upper(), event.source))
        if client.is_channel("#test.cz"):
            connection.join("#test.cz")

    def on_disconnect(self, connection, event):
        print('[{}] Disconnected to {}' .format(event.type.upper(), event.source))
        pass

    def on_pubmsg(self, connection, event):
        print('[{}] Pubmsg {}' .format(event.type.upper(), event.source))
        res = self.cursor.execute("""select * from `IRC_servers` where `Registred_users_userID` = 1;""", (self.userID,))

        if res != 0:
            print("Inserted successfully.")
            result = res.fetchall()
            print(result)
            res2 = self.cursor.execute("""select * from `IRC_channels` where `IRC_servers_serverID` = 1;""", (self.userID,))

        connection.privmsg(event.target, str(event.__dict__))

    def on_privmsg(self, connection, event):
        print('[{}] Privmsg {}' .format(event.type.upper(), event.source))
        connection.privmsg(event.target, str(event q.__dict__))

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




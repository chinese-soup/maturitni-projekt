#!/usr/bin/python3
# coding=utf-8

import os, sys, argparse

#irc library
from irc import client

class IRCSide(object):
    def __init__(self):
        super(IRCSide, self).__init__()

        self.client = client.Reactor()
        self.add_handlers()

        self.server_list_text = dict()
        self.server_list_instances = list()


        self.load_servers_from_db()

        self.connect_servers()



    def load_servers_from_db(self):
        self.server_list_text = [
            {"ip": "irc.freenode.org", "port": 6667, "use_ssl": False, "nickname": "test"},
            {"ip": "irc.stealth.net", "port": 6999, "use_ssl": True, "nickname": "test"}
        ]

    def add_handlers(self):
        self.client.add_global_handler('welcome', self.on_connect)
        self.client.add_global_handler('disconnect', self.on_disconnect)
        self.client.add_global_handler('nicknameinuse', self.on_nicknameinuse)
        self.client.add_global_handler('pubmsg', self.on_pubmsg)
        self.client.add_global_handler('privmsg', self.on_privmsg)
        self.client.add_global_handler('join', self.on_join)
        self.client.add_global_handler('part', self.on_part)
        self.client.add_global_handler('quit', self.on_quit)
        self.client.add_global_handler('nick', self.on_nick)



    def connect_server(self, _server, _port, _nickname):
        self.server_list_instances.append(self.client.server())
        self.server_list_instances[1:][0].connect(server=_server, port=_port, nickname=_nickname, password=None, username=None, ircname=None)


    def connect_servers(self):
        for srvr in self.server_list_text:
            self.connect_server(srvr["ip"], srvr["port"], srvr["nickname"])

    def start(self):
        pass

    def on_connect(self, connection, event):
        print('[{}] Connected to {}' .format(event.type.upper(), event.source))
        pass

    def on_disconnect(self, connection, event):
        print('[{}] Disconnected to {}' .format(event.type.upper(), event.source))
        pass

    def on_pubmsg(self, connection, event):
        print('[{}] Pubmsg {}' .format(event.type.upper(), event.source))
        pass

    def on_privmsg(self, connection, event):
        print('[{}] Privmsg {}' .format(event.type.upper(), event.source))
        pass

    def on_join(self, connection, event):
        print('[{}] Privmsg {}' .format(event.type.upper(), event.source))
        pass

    def on_part(self, connection, event):
        print('[{}] Privmsg {}' .format(event.type.upper(), event.source))
        pass

    def on_quit(self, connection, event):
        pass

    def on_nick(self, connection, event):
        pass

    def on_nicknameinuse(self, connection, event):
        pass

class WSocket(object):
    """WSocket"""
    def __init__(self, arg):
        super(WSocket, self).__init__()
        self.arg = arg




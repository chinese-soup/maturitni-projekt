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
class IRCSide(threading.Thread):
    def __init__(self, _userid):
        #super(IRCSide, self).__init__()
        threading.Thread.__init__(self)

        self.client = client.Reactor()
        self.add_handlers()

        self.server_list_instances = list()
        self.server_list_server_objects = list()

        self.load_servers_from_db()

        self.connect_servers()

        self.userID = _userid
        self.cau_ne = "cau"


        self.db = MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")
        self.cursor = self.db.cursor()
        self.func_to_be_threaded()
        self.client.process_forever()



    def _func_to_be_threaded(self):
        while(True):
            time.sleep(5)
            print("Sleep 5: ", self.userID)
            db_pull = MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")
            cursor_pull = db_pull.cursor()
            pull_result = cursor_pull.execute("""SELECT * FROM `IO_Table` WHERE `Registered_users_userID` = %s;""", (self.userID,))
            for result in pull_result:
                print(result)

            db_pull.close()


    def func_to_be_threaded(self):
        threading.Thread(target=self._func_to_be_threaded).start()


    """Loads user's servers from the database"""
    def load_servers_from_db(self):
        db = MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")
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
        self.client.add_global_handler("yourhost", self.on_your_host)
        self.client.add_global_handler("created", self.on_your_host)
        self.client.add_global_handler("myinfo", self.on_your_host)

        self.client.add_global_handler("nosuchnick", self.on_your_host)
        self.client.add_global_handler("nosuchcannel", self.on_your_host)
        self.client.add_global_handler("unknowncommand", self.on_your_host)
        self.client.add_global_handler("nonicknamegiven", self.on_your_host)
        self.client.add_global_handler("nicknameinuse", self.on_your_host)
        self.client.add_global_handler("nickcollison", self.on_your_host)
        self.client.add_global_handler("notonchannel", self.on_your_host)
        self.client.add_global_handler("useronchannel", self.on_your_host)

        self.client.add_global_handler("yourhost", self.on_your_host)
        self.client.add_global_handler("disconnect", self.on_disconnect)
        self.client.add_global_handler("nicknameinuse", self.on_nicknameinuse)
        self.client.add_global_handler("pubmsg", self.on_pubmsg)
        self.client.add_global_handler("privmsg", self.on_privmsg)
        self.client.add_global_handler("join", self.on_pubmsg)
        self.client.add_global_handler("part", self.on_pubmsg)
        self.client.add_global_handler("quit", self.on_pubmsg)
        self.client.add_global_handler("nick", self.on_nick)
        self.client.add_global_handler("action", self.on_pubmsg)

    def on_your_host(self, connection, event):
        print("test")

        if(len(event.arguments) != 0):
            message = event.arguments[0]
        else:
            message = str(event.arguments)

        res = self.cursor.execute("""SELECT * FROM `IRC_servers` WHERE `Registred_users_userID` = %s AND `serverID` = %s;""", (self.userID, connection.serverID))
        if res != 0:
            result = self.cursor.fetchall()
            print(result)
            serverID_res = int(result[0][0])
            print("serverID = {}".format(serverID_res))

            if serverID_res == int(connection.serverID): # pokud se získané ID z databáze rovná tomu, které v sobě
                # uchovává connection, redundantní check, ale just4safety
                res = self.cursor.execute("""INSERT INTO `IRC_other_messages` (IRC_servers_serverID,
                fromHostmask,
                messageBody,
                commandType,
                timeReceived)
                values (%s, %s, %s, %s, %s)""", (serverID_res, event.source, message, event.type.upper(),
                                                 datetime.datetime.utcnow()))
                self.db.commit()

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
                print("Error occurred.\nWhy: {0}".format(exp)) # TOOD: posílat takovéhle errory klientům

    """Called: never?"""
    def start(self):
        pass
    """
        Fired when any client successfully connects to an IRC server
    """
    def on_connect(self, connection, event):
        print('[{}] Connected to {}' .format(event.type.upper(), event.source))
        print("{}".format(event.arguments))

        res = self.cursor.execute("""SELECT * FROM `IRC_servers` WHERE `Registred_users_userID` = %s AND `serverID` = %s;""", (self.userID, connection.serverID))
        if res != 0:
            result = self.cursor.fetchall()
            print(result)

            serverID_res = int(result[0][0])

            res = self.cursor.execute("""UPDATE `IRC_servers` SET `isConnected` = %s WHERE `serverID` = %s;""", (1, serverID_res))

            print("RES: ",res)
            print("serverID = {}".format(serverID_res))

            if serverID_res == int(connection.serverID): # pokud se získané ID z databáze rovná tomu, které v sobě uchovává connection, redundantní check, ale JTS
                res = self.cursor.execute("""SELECT * FROM `IRC_channels` WHERE `IRC_servers_serverID` = %s;""", (serverID_res,))
                if res != 0:
                    result = self.cursor.fetchall()
                    print("Channmessage_windowels for serverID={}: {}".format(serverID_res, result))

                    channels = list()

                    for res in result:
                        channelID = res[0]
                        channelName = res[1]
                        channelPassword = res[2]
                        lastOpened = res[3]
                        channel_serverID = res[4]
                        temp_dict = {"channelName": channelName, "channelPassword": channelPassword}
                        channels.append(temp_dict)


                    for channel in channels:
                        if client.is_channel(channel["channelName"]):
                            connection.join(channel["channelName"], key=channel["channelPassword"])
                        else:
                            print("The channel in database is not a channel.")
                else:
                    print("[WARNING on_connect]: No channels to join on this server (serverID = {})".format(serverID_res))

    """Fired when any client is disconnected from an IRC server"""
    def on_disconnect(self, connection, event):
        print('[{}] Disconnected from {}' .format(event.type.upper(), event.source))
        print("{}".format(event.arguments))

        res = self.cursor.execute("""SELECT * FROM `IRC_servers` WHERE `Registred_users_userID` = %s AND `serverID` = %s;""", (self.userID, connection.serverID))
        if res != 0:
            result = self.cursor.fetchall()
            print(result)
            serverID_res = int(result[0][0])

            res = self.cursor.execute("""UPDATE `IRC_servers` SET `isConnected` = %s WHERE `serverID` = %s;""", (0, serverID_res))

            print("RES: ",res)
            print("serverID = {}".format(serverID_res))

    """Fired when any client gets a /ME message from any channel or query"""
    def on_action(self, connection, event):
        print('[{}] OnAction from {}' .format(event.type.upper(), event.source))


    """Fired when any client receives a message from a channel"""
    def on_pubmsg(self, connection, event):
        print("CONNECTION = {}\n\n".format(connection.__dict__))
        print('[{}] Pubmsg {} {}\n' .format(event.type.upper(), event.source, str(event.__dict__)))

        if(len(event.arguments) != 0):
            message = event.arguments[0]
        else:
            message = str(event.arguments)

        res = self.cursor.execute("""SELECT * FROM `IRC_servers` WHERE `Registred_users_userID` = %s AND `serverID` = %s;""", (self.userID, connection.serverID))
        if res != 0:
            result = self.cursor.fetchall()
            print(result)
            serverID_res = int(result[0][0])
            print("serverID = {}".format(serverID_res))

            if serverID_res == int(connection.serverID): # pokud se získané ID z databáze rovná tomu, které v sobě
                # uchovává connection, redundantní check, ale just4safety
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


"""
TODO: DELETE THIS
# Numeric table based on the Perl's Net::IRC.
numeric = {
    "001": "welcome",
    "002": "yourhost",
    "003": "created",
    "004": "myinfo",
    "005": "featurelist",  # XXX
    "200": "tracelink",
    "201": "traceconnecting",
    "202": "tracehandshake",
    "203": "traceunknown",
    "204": "traceoperator",
    "205": "traceuser",
    "206": "traceserver",
    "207": "traceservice",
    "208": "tracenewtype",
    "209": "traceclass",
    "210": "tracereconnect",
    "211": "statslinkinfo",
    "212": "statscommands",
    "213": "statscline",
    "214": "statsnline",
    "215": "statsiline",
    "216": "statskline",
    "217": "statsqline",
    "218": "statsyline",
    "219": "endofstats",
    "221": "umodeis",
    "231": "serviceinfo",
    "232": "endofservices",
    "233": "service",
    "234": "servlist",
    "235": "servlistend",
    "241": "statslline",
    "242": "statsuptime",
    "243": "statsoline",
    "244": "statshline",
    "250": "luserconns",
    "251": "luserclient",
    "252": "luserop",
    "253": "luserunknown",
    "254": "luserchannels",
    "255": "luserme",
    "256": "adminme",
    "257": "adminloc1",
    "258": "adminloc2",
    "259": "adminemail",
    "261": "tracelog",
    "262": "endoftrace",
    "263": "tryagain",
    "265": "n_local",
    "266": "n_global",
    "300": "none",
    "301": "away",
    "302": "userhost",
    "303": "ison",
    "305": "unaway",
    "306": "nowaway",
    "311": "whoisuser",
    "312": "whoisserver",
    "313": "whoisoperator",
    "314": "whowasuser",
    "315": "endofwho",
    "316": "whoischanop",
    "317": "whoisidle",
    "318": "endofwhois",
    "319": "whoischannels",
    "321": "liststart",
    "322": "list",
    "323": "listend",
    "324": "channelmodeis",
    "329": "channelcreate",
    "330": "whoisaccount", # <nick> <accountName> :<info> - Spawned from a /whois
    "331": "notopic",
    "332": "currenttopic",
    "333": "topicinfo",
    "341": "inviting",
    "342": "summoning",
    "346": "invitelist",
    "347": "endofinvitelist",
    "348": "exceptlist",
    "349": "endofexceptlist",
    "351": "version",
    "352": "whoreply",
    "353": "namreply",
    "354": "whospcrpl", # Response to a WHOX query
    "361": "killdone",
    "362": "closing",
    "363": "closeend",
    "364": "links",
    "365": "endoflinks",
    "366": "endofnames",
    "367": "banlist",
    "368": "endofbanlist",
    "369": "endofwhowas",
    "371": "info",
    "372": "motd",
    "373": "infostart",
    "374": "endofinfo",
    "375": "motdstart",
    "376": "endofmotd",
    "377": "motd2",        # 1997-10-16 -- tkil
    "381": "youreoper",
    "382": "rehashing",
    "384": "myportis",
    "391": "time",
    "392": "usersstart",
    "393": "users",
    "394": "endofusers",
    "395": "nousers",
    "401": "nosuchnick",
    "402": "nosuchserver", #nosuchnick, nosuchcannel, unknowncommand, nonicknamegiven, nicknameinuse, nickcollison, notonchannel, useronchannel
    "403": "nosuchchannel",
    "404": "cannotsendtochan",
    "405": "toomanychannels",
    "406": "wasnosuchnick",
    "407": "toomanytargets",
    "409": "noorigin",
    "410": "invalidcapcmd",
    "411": "norecipient",
    "412": "notexttosend",
    "413": "notoplevel",
    "414": "wildtoplevel",
    "421": "unknowncommand",
    "422": "nomotd",
    "423": "noadmininfo",
    "424": "fileerror",
    "431": "nonicknamegiven",
    "432": "erroneusnickname",  # Thiss iz how its speld in thee RFC.
    "433": "nicknameinuse",
    "436": "nickcollision",
    "437": "unavailresource",  # "Nick temporally unavailable"
    "441": "usernotinchannel",
    "442": "notonchannel",
    "443": "useronchannel",
    "444": "nologin",
    "445": "summondisabled",
    "446": "usersdisabled",
    "451": "notregistered",
    "461": "needmoreparams",
    "462": "alreadyregistered",
    "463": "nopermforhost",
    "464": "passwdmismatch",
    "465": "yourebannedcreep",  # I love this one...
    "466": "youwillbebanned",
    "467": "keyset",
    "471": "channelisfull",
    "472": "unknownmode",
    "473": "inviteonlychan",
    "474": "bannedfromchan",
    "475": "badchannelkey",
    "476": "badchanmask",
    "477": "nochanmodes",  # "Channel doesn't support modes"
    "478": "banlistfull",
    "480": "cannotknock", #generated when /knock <chan> is ran on a channel that you are either in or has /knock'ing disabled
    "481": "noprivileges",
    "482": "chanoprivsneeded",
    "483": "cantkillserver",
    "484": "restricted",   # Connection is restricted
    "485": "uniqopprivsneeded",
    "491": "nooperhost",
    "492": "noservicehost",
    "501": "umodeunknownflag",
    "502": "usersdontmatch",
}

codes = dict((v, k) for k, v in numeric.items())

generated = [
    "dcc_connect",
    "dcc_disconnect",
    "dccmsg",
    "disconnect",
    "ctcp",
    "ctcpreply",
]

protocol = [
    "error",
    "join",
    "kick",
    "mode",
    "part",
    "ping",
    "privmsg",
    "privnotice",
    "pubmsg",
    "pubnotice",
    "quit",
    "invite",
    "pong",
    "action",
    "topic",
    "nick",
]

"""


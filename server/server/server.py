#!/usr/bin/python3

import os, sys, argparse

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
        self.start_pull_thread()
        self.client.process_forever()

    def prepare_regexps(self):
        """
        Pre-compiles all regexs used on the server.
        TODO: Move to main.py?
        :return:
        """
        print("Preparing regular expressions for this session.")
        privmsg_parse = re.compile("")


    def _pull_thread(self):
        """
        Thread to pull IO data from the database to process and send to the main thread
        """
        while(True):
            db_pull = self.getDB()
            cursor_pull = db_pull.cursor()
            pull_result_code = cursor_pull.execute("""SELECT * FROM `IO_Table` WHERE `Registered_users_userID` = %s;""", (self.userID,))
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

                if data["commandType"] == "TEXTBOX":
                    message = data["argument1"]
                    if message[0] == "/" : # if the first character is a slash the user is trying to exec a command
                        print("Command.")


                    elif message[0] != "/":
                        print("Not command.")

                        for i in self.server_list_server_objects: # loop through all the server instances this user has
                            if(i.serverID == data["serverID"]): # if the server is the server we need
                                res = cursor_pull.execute("""SELECT * FROM `IRC_channels` WHERE `IRC_servers_serverID` = %s AND `channelID` = %s;""", (i.serverID, data["channelID"])) # get the IRC channel based on the ID
                                if res != 0:
                                    print("VíTĚZ")
                                    result = cursor_pull.fetchall()
                                    channelID_res = int(result[0][0])
                                    channelName_res = str(result[0][1]) # get the channelName from the query

                                    if i.is_connected() == True and data["channelID"] != -1: # if we are connected and the channelID is not -1 (broken)
                                        i.privmsg(channelName_res, message)

                                        res = cursor_pull.execute("""INSERT INTO `IRC_channel_messages` (IRC_channels_channelID,
                                                                    fromHostmask,
                                                                    messageBody,
                                                                    commandType,
                                                                    timeReceived)
                                                                    values (%s, %s, %s, %s, %s)""", (channelID_res, "polivecka!polivecka@polivecka", message, "PUBMSG", datetime.datetime.utcnow()))
                                        db_pull.commit()
                                        res = cursor_pull.execute("""DELETE FROM `IO_Table` WHERE `messageID` = %s;""", (data["messageID"],)) # delete the message we just processed
                                        db_pull.commit()
                                    else:
                                        res = cursor_pull.execute("""INSERT INTO `IRC_other_messages` (IRC_servers_serverID,
                                                        fromHostmask,
                                                        messageBody,
                                                        commandType,
                                                        timeReceived)
                                                        values (%s, %s, %s, %s, %s)""", (i.serverID, i.real_server_name, "You cannot write into server windows. If you want to send raw IRC use /RAW. If you want to message someone use /MSG or /PRIVMSG.", "CMD_ERROR" , datetime.datetime.utcnow()))
                                        db_pull.commit()

                                    #TOD: FIX HARDCODED STUFF
                                    #TODO: Change booleanm processed=TRUE
                elif data["commandType"] == "CONNECT_SERVER": # CONNECTING A NEW SERVER THAT HAS NOT BEEN ADDED TO THE LIST YET
                    reason = data["argument1"] # should we add it to the list of servers first or is it already loaded?
                    userID = data["userID"]
                    serverID = data["serverID"]
                    channelID = data["channelID"]
                    isAlreadyConnected = None
                    #test to see if the server is already in the list
                    for i in self.server_list_server_objects: # loop through all the server instances this user has
                        if(i.serverID == data["serverID"]):
                            isAlreadyConnected = i.is_connected()
                        else:
                            pass
                    if isAlreadyConnected == None:
                        print("Ještě neni v seznamu.")

                elif data["commandType"] == "JOIN_CHANNEL":
                    for i in self.server_list_server_objects: # loop through all the server instances this user has
                        if i.serverID == data["serverID"]: # if the server is the server we need
                            res = cursor_pull.execute("""SELECT * FROM `IRC_channels` WHERE `IRC_servers_serverID` = %s AND `channelID` = %s;""", (i.serverID, data["channelID"])) # get the IRC channel based on the ID
                            if res != 0:
                                print("VíTĚZ")
                                result = cursor_pull.fetchall()
                                channelID_res = int(result[0][0])
                                channelName_res = str(result[0][1]) # get the channelName from the query
                                channelKey_res = str(result[0][2])

                                if i.is_connected() == True and data["channelID"] != -1: # if we are connected and the channelID is not -1 (broken)
                                    i.join(channelName_res, key=channelKey_res) # TODO: track channels we are in?

                                res = cursor_pull.execute("""DELETE FROM `IO_Table` WHERE `messageID` = %s;""", (data["messageID"],)) # delete the message we just processed
                                db_pull.commit()

            time.sleep(2)
            print("Sleep2: ", self.userID)
            db_pull.close()

    def join_chnanel(self, data, cursor_pull):
        """
        Helper function for joining a channel
        :param data: dict
        """
        print("Helper")



    def start_pull_thread(self):
        """
        Starts the slave thread for pulling/inserting/changing new client IO from the database.
        """
        threading.Thread(target=self._pull_thread).start()


    def getDB(self):
        """
            Connects to the MySQL database and returns an SQL connection object
        :return: MySQLdb.connections.Connection
        """
        return MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")

    def load_servers_from_db(self):
        """
            Loads user's servers from the database on first load
        """
        db = self.getDB()
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

    def add_handlers(self):
        """
            Adds IRC handlers
        """
        self.client.add_global_handler("welcome", self.on_connect)
        self.client.add_global_handler("yourhost", self.on_your_host)
        self.client.add_global_handler("created", self.on_your_host)
        self.client.add_global_handler("myinfo", self.on_your_host)


        self.client.add_global_handler("nosuchnick", self.on_your_host)
        self.client.add_global_handler("nosuchcannel", self.on_your_host)
        self.client.add_global_handler("unknowncommand", self.on_your_host)
        self.client.add_global_handler("nonicknamegiven", self.on_your_host)
        self.client.add_global_handler("nickcollison", self.on_your_host)
        self.client.add_global_handler("notonchannel", self.on_your_host)
        self.client.add_global_handler("useronchannel", self.on_your_host)

        self.client.add_global_handler("nicknameinuse", self.on_your_host)


        self.client.add_global_handler("disconnect", self.on_disconnect)
        self.client.add_global_handler("nicknameinuse", self.on_nicknameinuse)
        self.client.add_global_handler("pubmsg", self.on_pubmsg)
        self.client.add_global_handler("privmsg", self.on_privmsg)
        self.client.add_global_handler("join", self.on_pubmsg)
        self.client.add_global_handler("part", self.on_pubmsg)
        self.client.add_global_handler("quit", self.on_pubmsg)
        self.client.add_global_handler("nick", self.on_nick)
        self.client.add_global_handler("action", self.on_pubmsg)

    def nickname_in_use(self, connection, event):
        print("self.nickname_in_use")

    def on_your_host(self, connection, event):
        """
            Handles several different commands the server sends upon connecting
        """
        print(event)
        print(event.arguments)

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

    def connect_server(self, _serverID, _server, _port, _nickname):
        """
            Called to connect to a specified server
        """
        temp_server_connection_object = self.client.server()

        temp_server_connection_object.serverID = _serverID # důležité: přidává serverID z databáze jako atribut do connection, které se používá při každém global_handleru definovaném o pář řádků výše

        print(temp_server_connection_object.serverID)
        #temp_server_connection_object.setServerID(_serverID)

        self.server_list_server_objects.append(temp_server_connection_object)
        self.server_list_instances.append(temp_server_connection_object.connect(server=_server, port=_port, nickname=_nickname, password=None, username=None, ircname=None))

    def connect_servers(self):
        """
            Called upon starting the instance
        """

        for srvr in self.server_list_text:
            try:
                self.connect_server(srvr["serverID"], srvr["serverIP"], int(srvr["serverPort"]), srvr["nickname"])
            except Exception as exp:
                print("Error occurred.\nWhy: {0}".format(exp)) # TOOD: posílat takovéhle errory klientům

    """Called: never?"""
    def start(self):
        pass

    def on_connect(self, connection, event):
        """
            Fired when any client successfully connects to an IRC server
        """
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

    def on_disconnect(self, connection, event):
        """
            Fired when any client is disconnected from an IRC server
        """

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

    def on_action(self, connection, event):
        """
            Fired when any client gets a /ME message from any channel or query
        """
        print('[{}] OnAction from {}' .format(event.type.upper(), event.source))


    def on_pubmsg(self, connection, event):
        """
            Fired when any client receives a message from a channel
        """
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
        """
            Fired upon receiving a private message.
        """
        print('[{}] Privmsg {}' .format(event.type.upper(), event.source))
        connection.privmsg(event.target, str(event.__dict__))

    def on_nick(self, connection, event):
        print('[{}] NickChange {}' .format(event.type.upper(), event.source))

    def on_nicknameinuse(self, connection, event):
        print('[{}] NickNameInUse {}' .format(event.type.upper(), event.source))

    def a_lot_more_to_be_implemneted(self, connection, event):
        print("save mefrom this nightmare")

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


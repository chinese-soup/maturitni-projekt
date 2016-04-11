#!/usr/bin/env python3
# coding=utf-8
# TODO: http://flask.pocoo.org/docs/0.10/patterns/packages/
# TODO2: http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/
# TODO3: Check for invalid data in forms

# db access library
import MySQLdb

# passlib for password hashing
from passlib.hash import sha512_crypt

# re for regular expressions parsing
import re

# randomness for session IDs
from os import urandom
from base64 import b64encode

from time import time
import datetime

import time

from flask import Flask, request, jsonify, redirect
app = Flask(__name__) # initializes the Flask app

from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

def is_email_valid(email_to_check):
    """Checks if a given email is valid"""
    regexp = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    result = re.match(regexp, str(email_to_check)) # if we conv to string we don't have to care about checking if the string is None and the regexp will just say it's not a valid email address
    if result is None:
        return False
    else:
        return True

def error(_status, _reason, _message):
    """
    :param _status: Status code (ok/error)
    :param _reason: A one word reason used in the chat.html javascript logic
    :param _message: A human-like message describing what went wrong (right).
    :return:
    """
    return jsonify(status=_status, reason=_reason, message=_message)

def get_userIP(request):
    """
        Gets the source IP from a request.
    :param request:
    :return:
    """
    return request.remote_addr


def _make_login_response(data_to_send, generated_sessionID):
    """
        This function sets a cookie header BEFORE sending off a successful /login response.
    """
    response = app.make_response(data_to_send)
    response.set_cookie("sessionid", value=generated_sessionID)
    response.headers.add("Access-Control-Allow-Origin", "localhost")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,Cookies")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE")
    return response



def get_userID_if_loggedin(request):
    """
    This function checks for a sessionID in the database and joins it with the userID of a user
    this is used to check if the user is allowed to request the data he's requesting
    aka if he's not trying to access data of a user with a different ID.

    :param request: Flask request object
    :return: userID if the user is loggedIn / False if the user is not logged in or an error occurred while trying to get the lgged in info from the database
    """


    if "sessionid" in request.cookies: # checks if the request even has a session cookie, otherwise return False
        session_id_cookie = request.cookies.get("sessionid") # get sessionID from a cookie
        db = MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")
        print("session_id_cookie = ", session_id_cookie)
        cursor = db.cursor()
        result_code = cursor.execute("""SELECT * FROM `User_sessions` WHERE `session_id` = %s""", (session_id_cookie,)) # look up the session cookie in the database and compare it to the request one
        if result_code is not 0:
            result = cursor.fetchone()
            session_id = result[0]
            userID = result[3]
            print(session_id, userID)
            if session_id == session_id_cookie:
                return userID
            else:
                return False
        else:
            return False
    else:
        return False


def check_if_serverID_belongs_to_userID(userID, serverID):
    """
    Checks if a given serverID belongs to a given userID and returns True/False
    :param userID:
    :param serverID:
    :return:
    """
    db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")

    cursor = db.cursor()
    result_code = cursor.execute("""SELECT * FROM `IRC_servers` WHERE `serverID` = %s AND `Registred_users_userID` = %s""", (serverID, userID,))
    if result_code is not 0:
        result = cursor.fetchone()

        serverID_result = result[0]
        userID_result = result[5]

        if serverID_result == serverID and userID_result == userID: # redundant check, but whatever, this app is already slow af, anyway
            return True
        else:
            return False
    return False

# after request, pro povoleni CORS requestů z javascriptu
@app.after_request
def after_request(response):
    """
    Adds CORS allowing headers to the response before sending it to the client.
    :param response: Flask response object
    :return: response: Flask response object with added CORS allowing headers
    """
    response.headers.add("Access-Control-Allow-Origin", "http://localhost") #TODO: localhost fix
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,Cookies")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE")
    response.headers.add("Access-Control-Allow-Credentials", "true")
    return response


@app.route("/")
def hello_world():
    """Defaultní routa"""
    if "sessionid" in request.cookies:
        print("request.cookies", request.cookies)
        asdf = dict(status="ok", message=str(request.cookies["sessionid"]))
        return jsonify(asdf)
    else:
        asdf = dict(status="ok", message="API is up.")
        return jsonify(asdf)

@app.route("/logout", methods=["POST"])
def logout():
    """User logout route"""
    if "sessionid" in request.cookies:
        db = MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")
        cookies_sessionid = request.cookies.get("sessionid") # get sessionID from a cookie
        cursor = db.cursor()
        result_code = cursor.execute("""SELECT * FROM `User_sessions` WHERE `session_id` = %s""", (cookies_sessionid,)) # look up the given session cookie in the database and compare it to the request one

        if result_code is not 0:
            session_id = cursor.fetchone()[0]
            session_id_cookie = request.cookies.get("sessionid")
            print("session_id DB:", session_id)
            print("session_id cookie:", cookies_sessionid)

            if session_id == session_id_cookie:
                cursor = db.cursor()
                result_code = cursor.execute("DELETE FROM `User_sessions` WHERE `session_id` = %s", (session_id,)) # delete the session cookie from database => logged out
                db.commit()
                db.close()

        # delete the cookie from client's browser, we delete it even if it isn't in the database. as he's trying to login with an invalid sessionid
        data = jsonify(status="ok", reason="loggedout", message="Logged out successfully.")
        response = app.make_response(data)
        response.set_cookie("sessionid", value="", expires=0) # adds a cookie removal header to the logout response

        return response
    else:
        return jsonify(status="error", reason="not_loggedin", message="You are not logged in.")


@app.route("/upon_login", methods=["POST"])
def upon_login():
    """
        Route called upon loading chat.html.
        Returns the email of the user if they are logged in.
        Returns a not_loggedin response if the user is not logged in.
    """
    userID = get_userID_if_loggedin(request)
    print("UserID = ", userID)
    if userID is not False:
        db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")

        cursor = db.cursor()
        cursor.execute("""SELECT (email) FROM `Registered_users` WHERE `userID` = %s""", (userID,))
        result = cursor.fetchone()
        _email = result[0] # 0 = email
        return jsonify(status="ok", reason="loggedin_email_status", message=_email)

    else:
        return jsonify(status="error", reason="not_loggedin", message="You are not logged in.")


@app.route("/check_session", methods=["GET", "POST"])
def check_session():
    """
        Route called upon loading login.html to check if the API is alive and if the user is logged in.
        Used to replace the login form on login.html with a button to continue to the main app site.
        Used to periodically check if the user is still logged in and does not need to be redirected away
        from chat.html
    """
    userID = get_userID_if_loggedin(request)

    if userID is not False:
        return jsonify(status="ok", reason="alive_loggedin", message=True)
    else:
        return jsonify(status="error", reason="alive_not_loggedin", message="You are not logged in.")

@app.route("/login", methods=["POST"])
def login():
    """
        Route called upon clicking Login on login.html
    :return:
    """
    _email = request.form.get("email").lower() # .lower() protože aHoJ je to samé jako ahoj => zabraňuje více registrací na jeden email
    _password = request.form.get("password")
    _hashed_password = sha512_crypt.encrypt(_password, salt="CodedSaltIsBad") # hash zadaného hesla

    db = MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")

    cursor = db.cursor()
    result_code = cursor.execute("""SELECT * FROM `Registered_users` WHERE `email` = %s AND `password` = %s""", (_email, _hashed_password))

    if result_code is not 0:
        values = cursor.fetchone()
        _id = values[0]

        if "sessionid" in request.cookies:
            cookies_sessionid = request.cookies.get("sessionid")
            cursor = db.cursor()
            result_code = cursor.execute("""SELECT * FROM `User_sessions` WHERE `Registred_users_userID` = %s""", (_id,))
            if result_code is not 0:
                session_id = cursor.fetchone()[0]

                session_id_cookie = request.cookies.get("sessionid")
                print("session_id DB:", session_id)
                print("session_id cookie:", session_id_cookie)

                if session_id == session_id_cookie:
                    print("At this point, we are already logged in. Redirect the user here!!!!")
                    return jsonify(status="ok", reason="already_loggedin", message="You are already logged in.")

            print("Reached the end of checking the session cookie with the one in DB.",
                  "The current cookie session does not exist. Gonna relog now.")

        # remove any original session we had (stupid, ofc means that a user gets only one session => no multiple instances of the app across browsers)
        cursor = db.cursor()
        result_code = cursor.execute("DELETE FROM `User_sessions` WHERE `Registred_users_userID` = %s", (_id,))
        db.commit()

        generated_sessionID = b64encode(urandom(64)).decode("utf-8") # generate a sessionID

        result_code = cursor.execute("""INSERT INTO `User_sessions` (session_id, Registred_users_userID) values (%s, %s)""", (generated_sessionID, _id), )
        db.commit()

        if result_code != 0:
            data_to_send = jsonify(status="ok", reason="cookie_ok", message="Logged in successfully.", sessionid=generated_sessionID)
            response = app.make_response(data_to_send)
            response.set_cookie("sessionid", value=generated_sessionID)
            #response.headers['Access-Control-Allow-Origin'] = "http://localhost"
            #response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,Cookies'
            #response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE'
            #response.headers['Access-Control-Allow-Credentials'] = 'true'

            #print("RESPONSE", response)
            return response
        else:
            return error("error", "loginerror", "An error occurred while trying to log you in.")

    elif result_code is 0:
        return error("error", "badlogin", "The login information you have provided is incorrect.<br>Check your email address and password and try again.")

    return error("error", "unknown_error", "REACHED END OF LOGIN() WITHOUT RETURNING BEFORE THAT, THIS SHOULD NEVER HAPPEN.")

# routa volaná při registraci na index.html
@app.route("/register", methods=["POST"])
def register():
    db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")
    _email = None
    _password = None
    try:
        _email = request.form.get("email").lower() or None
        _password = request.form.get("password") or None
    except:
        return jsonify(status="error", reason="email_invalid", message="The email address you have specified is invalid.")

    if is_email_valid(_email) == False: # FYI: checking for email's validness automatically already checks if it's empty
        return jsonify(status="error", reason="email_invalid", message="The email address you have specified is invalid.")
    if _password == None:
        return jsonify(status="error", reason="password_empty", message="The password is empty.")

    _email = str(_email).lower()
    _hashed_password = sha512_crypt.encrypt(_password, salt="CodedSaltIsBad") # hash the given password

    cursor = db.cursor()
    cursor.execute("""SELECT (email) FROM `Registered_users` WHERE `email` = %s;""", (_email,))
    exists_result = db.affected_rows()

    if exists_result is not 0:
        return jsonify(status="error", reason="account_exists", message="An account with this email address is already registered,<br>please login instead.")
    elif exists_result is 0:
        _result = cursor.execute("""INSERT INTO `Registered_users` (email, password, isActivated) values (%s, %s, %s);""", (_email, _hashed_password, 1),)
        db.commit()

        if _result == 1:
            return jsonify(status="ok", reason="reg_success", message="Your account was sucessfully registered. You can now login.")
        else:
            return jsonify(status="error", reason="insert_failed", message="Account registration failed.")
    else:
        return jsonify(status="error", reason="insert_failed", message="Account registration failed.")

# routa volaná při načtení chat.html
# routa volaná při přidání / odstranění serveru
@app.route("/get_server_list", methods=["GET", "POST"])
def get_server_list():
    """
    Route called upon loading chat.html, adding, removing and editing servers.
    :return:
    """
    userID = get_userID_if_loggedin(request)
    print("UserID = ", userID)

    if userID is not False:
        db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")
        cursor = db.cursor()
        res = cursor.execute("""SELECT * FROM `IRC_servers` WHERE `Registred_users_userID` = %s;""", (userID,))
        if res != 0:
            result = cursor.fetchall()
            # horrible hacks (to get around the fact that jsonify is stupid) follow: #
            #TODO: REWRITE BECAUSE IT IS NOT STUPID, I AM STUPID, SEE SOLUTION IN ROUTES BELOW #
            servers = dict()

            i = 0
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
                                    "useSSL": res[9],
                                    "channels": None}
                servers[i] = server_dict_temp
                i = i+1

            i = 0

            for srvr in servers.items(): # loop through servers in order to get the list of channels (TODO: Add queries)
                srvrID = int(srvr[1]["serverID"])
                cursor = db.cursor()
                res = cursor.execute("""SELECT * FROM `IRC_channels` WHERE `IRC_servers_serverID` = %s;""", (srvrID,))
                channel_result = cursor.fetchall()
                print("CHANNELS", channel_result)
                channels_list = list()

                for res in channel_result:
                    channel_dict_temp = {"channelID": res[0],
                                         "channelName": res[1],
                                         "channelPassword": res[2],
                                         "isJoined": res[3],
                                         "lastOpened": res[4],
                                         "serverID": res[5]}
                    channels_list.append(channel_dict_temp)

                servers[i]["channels"] = channels_list

                i = i+1

            response = {"status": "ok", "reason": "listing_servers", "message": servers}
            return jsonify(response)

        else:
            return error("ok", "no_servers_to_list", "No servers yet.")
    else:
        return error("error", "not_loggedin", "You are not logged in.")

@app.route("/add_channel", methods=["POST"])
def add_channel():
    """
    Routa called upon joining (adding) a new channel
    TODO: MOVE TO SERVER SIDE?
    :return: channel_added_sucessfully / channel_was_not_added / not_loggedin
    """
    userID = get_userID_if_loggedin(request)
    channelName = request.form.get("channelName") or None
    channelPassword = request.form.get("channelPassword") or ""
    serverID = request.form.get("serverID") or ""

    if userID is not False and channelName is not None:
        db = MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")
        cursor = db.cursor()

        # přidáme server
        res = cursor.execute("""INSERT INTO `IRC_channels` (channelName, channelPassword, IRC_servers_serverID, isJoined, lastOpened)
        values(%s, %s, %s, %s, CURRENT_TIMESTAMP) ON DUPLICATE KEY UPDATE `channelName` = `channelName`;""", (channelName, channelPassword, serverID, False))
        db.commit()
        if res == 1:
            response = {"status": "ok", "reason": "channel_added_sucessfully", "message": "Channel added successfully."}
        else:
            response = {"status": "ok", "reason": "channel_was_not_added", "message": "Channel cannot be added at this time."} # error?

        return jsonify(response)
        db.close()
    else:
        return error("error", "not_loggedin", "You are not logged in.")


# routa volaná při zobrazení okna globálních nastavení
@app.route("/get_global_settings", methods=["POST"])
def get_global_settings():
    """
    Route called to get the current global settings for when a user opens the settings dialog
    """
    userID = get_userID_if_loggedin(request)
    print("UserID = ", userID)
    if userID is not False:
        db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")
        cursor = db.cursor()
        res = cursor.execute("""SELECT * FROM `User_settings` WHERE `Registred_users_userID` = %s;""", (userID,))
        if res != 0:
            db.close()
            result = cursor.fetchall()
            global_settings = list(result)
            response = {"status": "ok", "reason": "listing_settings", "message": global_settings}
            print("SETTINGS LISTED")

            return jsonify(response)
        elif res == 0: # global settings row for this user doesn't exist, let's create it
            cursor = db.cursor()
            cursor.execute("""INSERT INTO `User_settings` (Registred_users_userID) values (%s);""", (userID,)) # vytvoří defaultní nastavení pro uživatele, který ještě nastavení nemá
            db.commit()

            res2 = cursor.execute("""SELECT * FROM `User_settings` WHERE `Registred_users_userID` = %s;""", (userID,)) # it's redundant to select the settings if we know that we just inserted the default ones, but just to be sure
            if res2 != 0:
                db.close()
                result = cursor.fetchall()
                global_settings = list(result)
                response = {"status": "ok", "reason": "listing_settings", "message": global_settings} # vratí nastavení, kterými se naplní formulář s nastavením
                return jsonify(response)
            else:
                db.close()
                return error("error", "db_error", "Database error.<br>Are you logged in?")
        else:
            return error("ok", "no_servers_to_list", "Error loading your current settings, please try again later.")
    else:
         return error("error", "not_loggedin", "You are not logged in.")


@app.route("/save_global_settings", methods=["POST"])
def set_global_settings():
    """
    Route called upon clicking the save button in the global settings dialog.
    :return: global_settings_saved / global_settings_not_saved / not_loggedin
    """
    userID = get_userID_if_loggedin(request)
    print("UserID = ", userID)
    if userID is not False:
        settings_cols_names = ["highlight_words", "whois_username", "whois_realname", "global_nickname", "show_joinpartquit_messages",
                              "show_seconds", "show_video_previews", "show_image_previews"]
        settings_cols_values = []

        # initialize list with values from the request
        for key in settings_cols_names:
            if(request.form.get(key) == "true"):
                settings_cols_values.append(1) # js<->python<->db fix true => 1
            elif(request.form.get(key) == "false"):
                settings_cols_values.append(0) # js<->python<->db fix false => 0
            else:
                settings_cols_values.append(request.form.get(key)) # if not boolean just add

        db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")
        cursor = db.cursor()
        res = cursor.execute("""INSERT INTO `User_settings` (highlight_words,
                                whois_username,
                                whois_realname,
                                global_nickname,
                                show_joinpartquit_messages,
                                show_seconds,
                                show_video_previews,
                                show_image_previews,
                                Registred_users_userID)
                                values (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON DUPLICATE KEY UPDATE highlight_words=%s,
                                whois_username=%s,
                                whois_realname=%s,
                                global_nickname=%s,
                                show_joinpartquit_messages=%s,
                                show_seconds=%s,
                                show_video_previews=%s,
                                show_image_previews=%s;""", (settings_cols_values[0],
                                                              settings_cols_values[1],
                                                              settings_cols_values[2],
                                                              settings_cols_values[3],
                                                              settings_cols_values[4],
                                                              settings_cols_values[5],
                                                              settings_cols_values[6],
                                                              settings_cols_values[7],
                                                              userID,
                                                              settings_cols_values[0],
                                                              settings_cols_values[1],
                                                              settings_cols_values[2],
                                                              settings_cols_values[3],
                                                              settings_cols_values[4],
                                                              settings_cols_values[5],
                                                              settings_cols_values[6],
                                                              settings_cols_values[7],))
        db.commit()
        print("RES", res)
        if res != 0:
            return error("ok", "global_settings_saved", "Global settings saved successfully.")
        else:
            return error("ok", "global_settings_notupdated", "No changes to save.")
            #return error("error", "global_settings_not_found", "Global settings failed to save.")
        db.close()
    else:
        return error("error", "not_loggedin", "You are not logged in.")



@app.route("/get_server_settings", methods=["POST"])
def get_server_settings():
    """
    Route called to prefill the inputs when a user edits a server.
    :return: listing_server_info / not_loggedin
    """
    userID = get_userID_if_loggedin(request)
    serverID = request.form.get("serverID") # gets the serverID of the server the user wants to edit from the ajax request

    print("UserID = ", userID)

    if userID is not False:
        db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")
        cursor = db.cursor()
        res = cursor.execute("""SELECT * FROM `IRC_servers` WHERE `Registred_users_userID` = %s AND `serverID` = %s;""", (userID, serverID))
        #res = cursor.execute("""SHOW COLUMNS FROM `IRC_servers`;""")
        result = cursor.fetchone()
        response = {"status": "ok", "reason": "listing_server_info", "message": result}
        db.close()
        return jsonify(response)
    else:
        return error("error", "not_loggedin", "You are not logged in.")



@app.route("/edit_server_settings", methods=["POST"])
def edit_server_settings():
    """
    Called to prefill the inputs when user edits a server
    :return: g
    """
    userID = get_userID_if_loggedin(request)
    serverID = request.form.get("serverID") # gets the serverID of the server the user wants to edit from the ajax request

    klice = {"serverName":"", "nickname":"", "serverPassword":"", "serverIP":"", "serverPort":"", "useSSL":""}
    for a in klice:
        klice[a] = request.form.get(a)

    print("UserID = ", userID)

    if userID is not False:
        db = MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")
        cursor = db.cursor()

        # zjitíme, zda server, který se uživatel snaží editovat je opravdu jeho
        res = cursor.execute("""SELECT Registred_users_userID,serverID FROM `IRC_servers` WHERE `Registred_users_userID` = %s AND `serverID` = %s;""", (userID, serverID))
        result = cursor.fetchone()
        if int(result[0]) == int(userID) and int(result[1]) == int(serverID):
            print("This is userID's server. yeah boy.")
            res = cursor.execute("""UPDATE `IRC_servers` SET serverName=%s,
                                 nickname=%s,
                                 serverPassword=%s,
                                 serverIP=%s,
                                 serverPort=%s,
                                 useSSL=%s WHERE `serverID` = %s;""", (klice["serverName"], klice["nickname"], klice["serverPassword"], klice["serverIP"], klice["serverPort"], klice["useSSL"], serverID))

            db.commit()
            if res == 1:
                response = {"status": "ok", "reason": "server_settings_edited_successfully", "message": "Server settings edited successfully.<br>Sending reconnect request."}
            else:
                response = {"status": "ok", "reason": "server_settings_not_edited", "message": "Server settings were not updated."} # error?

        db.close()
        return jsonify(response)
    else:
        return error("error", "not_loggedin", "You are not logged in.")

@app.route("/add_new_server_settings", methods=["POST"])
def add_new_server_settings():
    """
    Called upon saving a new IRC server in the add server dialog.
    """
    userID = get_userID_if_loggedin(request)

    if userID is not False:
        db = MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")
        cursor = db.cursor()
        klice = {"serverName":"", "nickname":"", "serverPassword":"", "serverIP":"", "serverPort":"", "useSSL":""}
        for a in klice:
            klice[a] = request.form.get(a)
        # přidáme server
        res = cursor.execute("""INSERT INTO `IRC_servers`
                                (Registred_users_userID, serverName, nickname, serverPassword, serverIP, serverPort, useSSL, serverSessionID, isAway, isConnected)
                                values(%s, %s, %s, %s, %s, %s, %s, -1, 0, 0);""",
                             (userID, klice["serverName"], klice["nickname"], klice["serverPassword"], klice["serverIP"], klice["serverPort"], klice["useSSL"]))
        db.commit()

        if res == 1:
            response = {"status": "ok", "reason": "server_settings_edited_successfully", "message": "Server settings edited successfully.<br>Sending reconnect request."}
        else:
            response = {"status": "ok", "reason": "server_settings_not_edited", "message": "Server settings were not updated."} # error?

        return jsonify(response)
    else:
        return error("error", "not_loggedin", "You are not logged in.")


@app.route("/get_messages", methods=["POST"])
def get_messages():
    """
    Route called to get new messages from a channel since time
    Route called to get old messages from a channel to fill the backlog
    :param backlog: true/false
    :param channelID: which channel should we get the messages for
    :param messageLimit: change the amount of messages if loading backlog
    :return:
    """
    userID = get_userID_if_loggedin(request)
    print("UserID = ", userID)
    try:
        backlog = bool(int(request.form.get("backlog"))) # rozhoduje zda budeme vracet backlog nebo nejnovější zprávy od minule
        channelID = request.form.get("channelID") # channelID
        messageLimit = int(request.form.get("limit")) or 20 # limit zpráv, které získáváme z db
    except Exception as ex:
        print("Error trying to get form data @ get_messages(): {0}".format(ex))
        return error("error", "bad_request", "Bad API request.")

    if userID is not False:
        db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")
        cursor = db.cursor()

        res = cursor.execute("""SELECT * FROM `IRC_channels` WHERE `channelID` = %s;""", (channelID,)) #query to find the serverID so we can check if the user owns this serverID and is not trying to read something that is not his
        if res != 0:
            result = cursor.fetchone()
            serverID_result = int(result[5]) # 5 = IRC_servers_serverID

            if check_if_serverID_belongs_to_userID(userID, serverID_result) is True:

                if backlog is True: # if we want to load messages for a channel we are opening for the first time this session
                    res = cursor.execute("""
                    (SELECT *
                    FROM `IRC_channel_messages`
                    WHERE `IRC_channels_channelID` = %s
                    ORDER BY `messageID` DESC LIMIT %s)
                    ORDER BY `messageID` ASC;""", (channelID, messageLimit)
                                         ) # query to get the backlog if the message window was opened just now
                    if res != 0:
                        result = cursor.fetchall()
                        messages = list()

                        for res in result:
                            print(res)
                            dateTime = res[4]
                            print("dateTime = ", dateTime)
                            utc_time = time.mktime(dateTime.timetuple()) * 1000 #  TODO: Fix UTC

                            server_dict_temp = {"messageID": res[0],
                                "fromHostmask": res[1],
                                "messageBody": res[2],
                                "commandType": res[3],
                                "timeReceived": utc_time,
                                "seen": res[5], # TODO: useless?
                                "IRC_channels_channelID": res[6]}
                            messages.append(server_dict_temp)
                            print(type(res[4]))
                        db.close()
                        response = {"status": "ok", "reason": "listing_messages", "message": messages}
                        return jsonify(response)
                    else:
                        return error("error", "no_messages_in_backlog", "There are no messages in this channel yet")

                else:
                    messageLimit = 10000000 # dummy, todo: fix? nah no time lol
                    sinceTimestamp = request.form.get("sinceTimestamp") # load messages posted since a given time

                    res = cursor.execute("""
                    (SELECT * FROM `IRC_channel_messages`
                    WHERE `IRC_channels_channelID` = %s
					AND `messageID` > %s
                    ORDER BY `messageID` DESC LIMIT %s)
                    ORDER BY `messageID` ASC;
                    """, (channelID, sinceTimestamp, messageLimit)
                                         ) #
                    if res != 0:
                        result = cursor.fetchall()
                        messages = list()

                        for res in result:
                            print(res)
                            dateTime = res[4]
                            utc_time = time.mktime(dateTime.timetuple()) * 1000

                            server_dict_temp = {"messageID": res[0],
                                "fromHostmask": res[1],
                                "messageBody": res[2],
                                "commandType": res[3],
                                "timeReceived": utc_time,
                                "seen": res[5],
                                "IRC_channels_channelID": res[6]}
                            messages.append(server_dict_temp)
                            print(type(res[4]))
                        db.close()
                        response = {"status": "ok", "reason": "listing_new_messages", "message": messages}
                        return jsonify(response)
                    else:
                        db.close()
                        response = {"status": "ok", "reason": "no_new_messages", "message": "No new messages since"}
                        return jsonify(response)

            else:
                db.close()
                return error("error", "channel_is_not_yours", "A channel with this channelID does not belong to your account.")


        else:
            db.close()
            return error("error", "channelid_does_not_exist", "A channel with the requested channelID does not exist.")
    else:
         return error("error", "not_loggedin", "You are not logged in.")


# TODO: fix sql?
@app.route("/get_server_messages", methods=["POST"])
def get_server_messages():
    """
    Route called to get new server messages for all servers since time
    Route called to get old server messages for all serversto fill the backlog
    :return:
    """
    userID = get_userID_if_loggedin(request)
    print("UserID = ", userID)

    backlog = bool(int(request.form.get("backlog"))) # rozhoduje zda budeme vracet backlog nebo nejnovější zprávy od minulého updatu

    serverID = request.form.get("serverID") # TODO: smazat?
    messageLimit = int(request.form.get("limit")) or 20 # limit zpráv, které získáváme z db

    if userID is not False:
        db = MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")
        cursor = db.cursor()

        res = cursor.execute("""SELECT serverID, serverName, Registred_users_userID FROM `IRC_servers` WHERE `Registred_users_userID` =
        %s;""", (userID,)) # get user's messages

        all_serverIDs_for_this_user = cursor.fetchall()
        print("all_serverIDs_for_this_user= ", all_serverIDs_for_this_user)

        messages = list()
        if backlog is True: # if we want to load messages for a channel we are opening for the first time this session
            for current_server in all_serverIDs_for_this_user:
                print("CURRENT_SERVER = ", current_server)
                serverID_result = int(current_server[0]) # 0 = serverID
                serverName_result = str(current_server[1]) # 1 = serverName

                res = cursor.execute("""
                (SELECT *
                FROM `IRC_other_messages`
                WHERE `IRC_servers_serverID` = %s
                ORDER BY `messageID` DESC LIMIT %s)
                ORDER BY `messageID` ASC;""", (serverID_result, messageLimit)
                                     ) # query to get the backlog if the message window was opened just now

                if res != 0:
                    result = cursor.fetchall()

                    for res in result:
                        print(res)
                        if check_if_serverID_belongs_to_userID(userID, int(res[6])) is True:
                            print("THIS IS YOUR SERVER")
                            dateTime = res[4]
                            print("dateTime = ", dateTime)

                            utc_time = time.mktime(dateTime.timetuple()) * 1000

                            server_dict_temp = {"messageID": res[0],
                                "fromHostmask": res[1],
                                "messageBody": res[2],
                                "commandType": res[3],
                                "timeReceived": utc_time,
                                "seen": res[5],
                                "IRC_servers_serverID": res[6],
                                "serverName": serverName_result}
                            messages.append(server_dict_temp)
                            print(type(res[4]))

                else:
                    pass # PASS HERE, BECAUSE THE SERVER MIGHT NOT HAVE ANY MESSAGES YET

        else:
            messageLimit = 10000000 # dummy, todo: fix? nah no time lol
            sinceTimestamp = request.form.get("sinceTimestamp") or -1 # load messages posted since a given ID

            res = cursor.execute("""
            (SELECT *
            FROM `IRC_other_messages`
            WHERE `messageID` > %s
            ORDER BY `messageID` DESC LIMIT %s)
            ORDER BY `messageID` ASC;
            """, (sinceTimestamp, messageLimit)) #

            if res != 0:
                result = cursor.fetchall()
                for res in result:
                    if check_if_serverID_belongs_to_userID(userID, int(res[6])) is True:
                        print(res)
                        dateTime = res[4]
                        utc_time = time.mktime(dateTime.timetuple()) * 1000

                        server_dict_temp = {"messageID": res[0],
                            "fromHostmask": res[1],
                            "messageBody": res[2],
                            "commandType": res[3],
                            "timeReceived": utc_time,
                            "seen": res[5],
                            "IRC_servers_serverID": res[6]}
                        messages.append(server_dict_temp)
            else:
                #db.close()
                #response = {"status": "ok", "reason": "no_new_messages", "message": "No new messages since {
                # 0}".format(sinceTimestamp)}
                #return jsonify(response)
                pass # if there are no messages, just pass, deal with it later

        db.close()
        if(len(messages) != 0):
            response = {"status": "ok", "reason": "listing_other_messages", "message": messages}
        else:
            response = {"status": "ok", "reason": "no_new_messages", "message": "No new messages since"}
        return jsonify(response)
    else:
         return error("error", "not_loggedin", "You are not logged in.")



@app.route("/send_io", methods=["POST"])
def send_io():
    """
    Route called to add an IO request to the database for the server backend to process.
    :return:
    """
    userID = get_userID_if_loggedin(request)
    ioType = request.form.get("ioType") or "error"
    channelID = request.form.get("channelID") or -1 # channelID
    serverID = request.form.get("serverID") or -1

    if userID is not False:
        db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")
        cursor = db.cursor()

        res = cursor.execute("""SELECT * FROM `IRC_channels` WHERE `channelID` = %s;""", (channelID,)) #query to find the serverID so we can check if the user owns this serverID and is not trying to read something that is not his
        if res != 0:
            chaninfo = cursor.fetchone()

            channelID_result = chaninfo[0] #channelID
            serverID = chaninfo[5] #ServerID

            result_code = cursor.execute("""SELECT * FROM `IRC_servers` WHERE `serverID` = %s AND `Registred_users_userID` = %s""", (serverID, userID,))
            if result_code is not 0:
                result = cursor.fetchone()
                serverID_result = result[0]
                userID_result = result[5]
                argument1 = ""
                argument2 = ""
                argument3 = ""
                timeSent = None
                processed = None


                if(ioType == "CONNECT_SERVER"):
                    argument1 = ""
                elif(ioType == "RECONNECT_SERVER"):
                    argument1 = ""
                elif(ioType == "REMOVE_SERVER"):
                    print("REMOVE_SERVER")
                elif(ioType == "PART_CHANNEL"):
                    print("PART CHANNEL")

                cursor.execute("""INSERT INTO `IO_Table` (Registred_users_userID,
                                                        commandType,
                                                        argument1,
                                                        argument2,
                                                        argument3,
                                                        timeSent,
                                                        processed,
                                                        fromClient,
                                                        serverID,
                                                        channelID)

                                                        values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (userID_result, argument1, argument2, argument3, timeSent, processed, True, serverID_result,
                      channelID_result))
                db.commit()
                db.close()
                response = {"status": "ok", "reason": "aha_obiku", "message": "UmŘÍT"}
                return jsonify(response)

@app.route("/send_textbox_io", methods=["POST"])
def send_textbox_io():
    """
    Route called to add an IO request invoked from the textbox to the database for the server backend to process.
    :return:
    """
    userID = get_userID_if_loggedin(request)
    channelID = int(request.form.get("channelID")) or -1 # channelID
    serverID = int( request.form.get("serverID")) or -1 # serverID
    print("SERVER ID JE {0}".format(serverID))
    textBoxData = str(request.form.get("textBoxData")) or "" # textBoxData

    print("do kundy: channelID {} serverID {} textBoxData {}".format(channelID, serverID, textBoxData))

    print("UserID = ", userID)
    db = MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30, charset="utf8")
    cursor = db.cursor()
    #channelID -1 serverID 1 textBoxData asdf
    if userID is not False and textBoxData != "" and channelID != -1: # if user is logged in & textboxdata has content and channelID was sent and serverID was not send (aka the command was sent while a channel or a query was open)

        result_code = cursor.execute("""SELECT * FROM `IRC_channels` WHERE `channelID` = %s;""", (channelID,)) #query to find the serverID so we can check if the user owns this serverID and is not trying to read something that is not his
        if result_code is not 0:
            chaninfo = cursor.fetchone()

            channelID_result = chaninfo[0] #channelID
            serverID = chaninfo[5] #ServerID

            result_code = cursor.execute("""SELECT * FROM `IRC_servers` WHERE `serverID` = %s AND `Registred_users_userID` = %s""", (serverID, userID,))
            if result_code is not 0:
                result = cursor.fetchone()
                serverID_result = result[0]
                userID_result = result[5]
                commandType = "TEXTBOX"

                argument1 = textBoxData
                argument2 = ""
                argument3 = ""
                timeSent = None
                processed = False


                res = cursor.execute("""INSERT INTO `IO_Table` (Registered_users_userID,
                                                        commandType,
                                                        argument1,
                                                        argument2,
                                                        argument3,
                                                        timeSent,
                                                        processed,
                                                        fromClient,
                                                        serverID,
                                                        channelID)

                                                        values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (userID_result, commandType, argument1, argument2, argument3, timeSent, processed, True,
                      serverID_result, channelID_result))
                db.commit()
                db.close()
                response = {"status": "ok", "reason": "textbox_io_channel_window_inserted", "message": "Di do píče"}
                return jsonify(response)
        else:
            return error("error", "channel_not_found", "Channel does not exist.")
    #channelID -1 serverID 1 textBoxData asdf
    elif userID is not False and textBoxData != "" and serverID != -1:
        result_code = cursor.execute("""SELECT * FROM `IRC_servers` WHERE `serverID` = %s AND `Registred_users_userID` = %s""", (serverID, userID,))
        if result_code is not 0:
            result = cursor.fetchone()
            serverID_result = result[0]
            userID_result = result[5]
            commandType = "TEXTBOX"

            argument1 = textBoxData
            argument2 = ""
            argument3 = ""
            timeSent = None
            processed = False

            res = cursor.execute("""INSERT INTO `IO_Table` (Registered_users_userID,
                                                    commandType,
                                                    argument1,
                                                    argument2,
                                                    argument3,
                                                    timeSent,
                                                    processed,
                                                    fromClient,
                                                    serverID,
                                                    channelID)

                                                    values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (userID_result, commandType, argument1, argument2, argument3, timeSent, processed, True,
                  serverID_result, -1))
            db.commit()
            db.close()
            response = {"status": "ok", "reason": "textbox_io_server_window_inserted", "message": res}
            return jsonify(response)

        else:
            return error("error", "server_does_not_exist", "Server does not exist.")
    else:
        print("AHOJ")
        return error("error", "not_loggedin", "You are not logged in.")


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0") # TODO: remove binding on all interfaces; this is only here for debugging



#!/usr/bin/env python3
# coding=utf-8
# neumim programovat
# TODO: http://flask.pocoo.org/docs/0.10/patterns/packages/
# TODO: http://flask.pocoo.org/docs/0.10/patterns/packages/
# TODO: http://flask.pocoo.org/docs/0.10/patterns/packages/
# TODO: http://flask.pocoo.org/docs/0.10/patterns/packages/
# TODO: http://flask.pocoo.org/docs/0.10/patterns/packages/
# TODO: http://flask.pocoo.org/docs/0.10/patterns/packages/
# TODO: http://flask.pocoo.org/docs/0.10/patterns/packages/
# TODO: http://flask.pocoo.org/docs/0.10/patterns/packages/
# TODO: http://flask.pocoo.org/docs/0.10/patterns/packages/
# TODO: http://flask.pocoo.org/docs/0.10/patterns/packages/
# TODO: http://flask.pocoo.org/docs/0.10/patterns/packages/
# TODO2: http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/
# TODO2: http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/
# TODO2: http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/
# TODO2: http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/
# TODO2: http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/
# TODO2: http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/
# TODO2: http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/
# TODO2: http://flask.pocoo.org/docs/0.10/deploying/mod_wsgi/
# TODO3: Check for invalid data in forms
# TODO3: Check for invalid data in forms
# TODO3: Check for invalid data in forms
# TODO3: Check for invalid data in forms
# TODO3: Check for invalid data in forms


# db access lib
import MySQLdb

# passlib for password hashing
from passlib.hash import sha512_crypt

# re for regular expressions parsing
import re

# randomness for session IDs
from os import urandom
from base64 import b64encode
from time import time

from flask import Flask, request, jsonify, redirect
app = Flask(__name__)


from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

def is_email_valid(email_to_check): # TODO: maybe move to api_utils or sth??????
    regexp = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    result = re.match(regexp, str(email_to_check)) # if we conv to string we don't have to care about checking if the string is None and the regexp will just say it's not a valid email address, i will forever wonder what is faster, probably checking for None, but we may never be sure and I am too lazy to test it out so instead I am writing out this long comment on a single line without word wrapping just to calm myself down
    if result is None:
        return False
    else:
        return True

def error(_status, _reason, _message):
    return jsonify(status=_status, reason=_reason, message=_message)

def get_userIP(request):
    return request.remote_addr

def _make_login_response(data_to_send, generated_sessionID):
    response = app.make_response(data_to_send)
    response.set_cookie("sessionid", value=generated_sessionID)
    response.headers.add("Access-Control-Allow-Origin", "localhost")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,Cookies")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE")
    return response


# this function checks for a sessionID in the database and joins it with the userID of a user #
# this is used to check if the user is allowed to request the data he's requesting #
# aka if he's not trying to access data of a user with a different ID #

def get_userID_if_loggedin(request):
    if "sessionid" in request.cookies:
        session_id_cookie = request.cookies.get("sessionid")
        db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30)
        print("session_id_cookie = ", session_id_cookie)
        cursor = db.cursor()
        result_code = cursor.execute("""SELECT * FROM `User_sessions` WHERE `session_id` = %s""", (session_id_cookie,))
        if result_code is not 0:
            result = cursor.fetchone()
            session_id = result[0]
            userID = result[3]
            print("MRDKY: ")
            print(session_id, userID)
            if session_id == session_id_cookie:
                return userID
            else:
                return False
        else:
            return False
    else:
        return False


@app.after_request
def after_request(response):
  response.headers.add("Access-Control-Allow-Origin", "http://localhost")
  response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,Cookies")
  response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE")
  response.headers.add("Access-Control-Allow-Credentials", "true")
  return response

@app.route("/")
def hello_world():
    if "sessionid" in request.cookies:
        print("request.cookies", request.cookies)
        asdf = dict(status="ok", message=str(request.cookies["sessionid"]))
        return jsonify(asdf)
    else:
        asdf = dict(status="ok", message="API is up.")
        return jsonify(asdf)

@app.route("/logout", methods=["POST"])
def logout():
    if "sessionid" in request.cookies:
        db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30)
        cursor = db.cursor()
        cookies_sessionid = request.cookies.get("sessionid")
        cursor = db.cursor()
        result_code = cursor.execute("""SELECT * FROM `User_sessions` WHERE `session_id` = %s""", (cookies_sessionid,))

        print("session_id cookie:", cookies_sessionid)

        if result_code is not 0:
            session_id = cursor.fetchone()[0]
            session_id_cookie = request.cookies.get("sessionid")
            print("session_id DB:", session_id)
            print("session_id cookie:", cookies_sessionid)

            if session_id == session_id_cookie:
                cursor = db.cursor()
                # delete the session cookie from database
                result_code = cursor.execute("DELETE FROM `User_sessions` WHERE `session_id` = %s", (session_id,))
                db.commit()
                db.close()

        print("Reached the end of checking the session cookie with the one in DB.",
              "The current cookie session does not exist (anymore). The user is logged out.",
              "It's time to remove his cookie.")

        # delete the cookie from client's browser, we delete it even if it isn't in the database. as he's trying to login with an invalid sessionid
        data = jsonify(status="ok", reason="loggedout", message="Logged out successfully.")
        response = app.make_response(data)
        response.set_cookie("sessionid", value="", expires=0)
        #response.headers.add('Access-Control-Allow-Origin', "http://localhost")
        #response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Cookies')
        #response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
        #response.headers.add('Access-Control-Allow-Credentials', 'true')

        return response
    else:
         return jsonify(status="error", reason="not_loggedin", message="You are not logged in.")

# routa volaná při načtení chat.html pro ověření, zda je uživatel přihlášen
@app.route("/upon_login", methods=["POST"])
def upon_login():
    userID = get_userID_if_loggedin(request)
    print("UserID = ", userID)
    if userID is not False:
        db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30)
        print("Hello boys")
        cursor = db.cursor()
        cursor.execute("""SELECT (email) FROM `Registered_users` WHERE `userID` = %s""", (userID,))
        result = cursor.fetchone()
        _email = result[0]
        print("Email" + _email)
        return jsonify(status="ok", reason="loggedin_email_status", message=_email)

    else:
        return jsonify(status="error", reason="not_loggedin", message="You are not logged in.")

# routa volaná při přihlášení na login.html
@app.route("/login", methods=["POST"])
def login():
    _email = request.form.get("email").lower() # WARNING: make lower() because USER@EXAMPLE.COM is the same as UsER@eXamPle.com !!!!!
    _password = request.form.get("password")
    _hashed_password = sha512_crypt.encrypt(_password, salt="CodedSaltIsBad")

    db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30)

    cursor = db.cursor()
    result_code = cursor.execute("""SELECT * FROM `Registered_users` WHERE `email` = %s AND `password` = %s""", (_email, _hashed_password))

    if result_code is not 0: # use "is not" for extra speed (not like it matters, all code around here is slow anyway)
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

        # remove any original session we had (stupid, but whatever, I'd rather pass my last year of high school than have a good session system
        cursor = db.cursor()
        result_code = cursor.execute("DELETE FROM `User_sessions` WHERE `Registred_users_userID` = %s", (_id,))
        db.commit()

        generated_sessionID = b64encode(urandom(64)).decode("utf-8")
        print("Generated sessionID", generated_sessionID)

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

    return jsonify(status="error", message="REACHED END OF LOGIN() WITHOUT RETURNING BEFORE THAT, THIS SHOULD NEVER HAPPEN.")

# routa volaná při registraci na index.html
@app.route("/register", methods=["POST"])
def register():
    db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30)
    _email = None
    _password = None
    try:
        _email = request.form.get("email").lower() or None # WARNING: make lower() because USER@EXAMPLE.COM is the same as UsER@eXamPle.com !!!!!
        _password = request.form.get("password") or None
    except:
        return jsonify(status="error", reason="email_invalid", message="The email address you have specified is invalid.")

    if is_email_valid(_email) == False: # checking for email's validness automatically already checks if it's empty
        return jsonify(status="error", reason="email_invalid", message="The email address you have specified is invalid.")
    if _password == None:
        return jsonify(status="error", reason="password_empty", message="The password is empty.")

    _email = str(_email).lower()
    _hashed_password = sha512_crypt.encrypt(_password, salt="CodedSaltIsBad")

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
# split with get_channel_list?
@app.route("/get_server_list", methods=["GET", "POST"])
def get_server_list():
    userID = get_userID_if_loggedin(request)
    print("UserID = ", userID)

    if userID is not False:
        db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30)
        cursor = db.cursor()
        res = cursor.execute("""SELECT * FROM `IRC_servers` WHERE `Registred_users_userID` = %s;""", (userID,))
        if res != 0:
            result = cursor.fetchall()
            # horrible hacks to get aronud the fact that jsonify is stupid (imo) follow: #
            servers = dict()
            channels = dict()

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
            for srvr in servers.items():
                print(srvr)
                srvrID = srvr[1]["serverID"]
                cursor = db.cursor()
                res = cursor.execute("""SELECT * FROM `IRC_channels` WHERE `IRC_servers_serverID` = %s;""", (srvrID,))
                channel_result = cursor.fetchall()
                print(channel_result)

                for res in channel_result:
                    channel_dict_temp = {"channelID": res[0],
                                         "channelName": res[1],
                                         "channelPassword": res[2],
                                         "isJoined": res[3],
                                         "lastOpened": res[4],
                                         "serverID": res[5]}

                    servers[i]["channels"] = channel_dict_temp

                i = i+1

            response = {"status": "ok", "reason": "listing_servers", "message": servers}
            return jsonify(response)

        else:
            return error("ok", "no_servers_to_list", "No servers yet.")

        #return error("error", "debug", result)
    else:
        return error("error", "not_loggedin", "You are not logged in.")

# routa volaná při volbě kanálu ze seznamu, routa volaná při scrollnutí nahoru v chatovacím okénku pro získání více zpráv z minulosti
@app.route("/get_messages")
def get_messages():
    return "get_messages()"


# routa volaná při zobrazení okna globálních nastavení
@app.route("/get_global_settings", methods=["POST"])
def get_global_settings():
    userID = get_userID_if_loggedin(request)
    print("UserID = ", userID)
    if userID is not False:
        db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30)
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
            # TODO: Consider removing this and creating the insert on /register
            # TODO: Consider removing this and creating the insert on /register
            # TODO2: ALSO CONSIDER SETTING THE USER_SETTINGS TABLE'S DEFAULT VALUES INSTEAD OF INSERTING STUPID SHIT LIKE THIS #

            cursor = db.cursor()
            cursor.execute("""INSERT INTO `User_settings` (Registred_users_userID) values (%s);""", (userID,)) # generate default values for user's global settings
            db.commit()

            res2 = cursor.execute("""SELECT * FROM `User_settings` WHERE `Registred_users_userID` = %s;""", (userID,)) # it's redundant to select the settings if we know that we just inserted the default ones, but just to be sure
            if res2 != 0:
                db.close()
                result = cursor.fetchall()
                global_settings = list(result)
                response = {"status": "ok", "reason": "listing_settings", "message": global_settings}
                return jsonify(response)
            else:
                db.close()
                return error("error", "db_error", "Database error.<br>Are you logged in?")
        else:
            return error("ok", "no_servers_to_list", "Error loading your current settings, please try again later.")
    else:
         return error("error", "not_loggedin", "You are not logged in.")

# routa volaná při uložení globálních nastavení v okně nastavení globálních nastavení
@app.route("/save_global_settings", methods=["POST"])
def set_global_settings():
    userID = get_userID_if_loggedin(request)
    print("UserID = ", userID)
    if userID is not False:
        settings_cols_names = ["highlight_words", "whois_username", "whois_realname", "global_nickname", "show_joinpartquit_messages",
                              "show_seconds", "show_video_previews", "show_image_previews"]
        settings_cols_values = []

        for key in settings_cols_names:
            # fix boolean values
            if(request.form.get(key) == "true"):
                settings_cols_values.append(1)
            elif(request.form.get(key) == "false"):
                settings_cols_values.append(0)
            else:
                settings_cols_values.append(request.form.get(key))

        print("SETTINGS", settings_cols_names, "\n", settings_cols_values)

        db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30)
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





# routa volaná při načtení chat.html
# routa volaná při přidání / odstranění serveru
# split with get_channel_list?
@app.route("/get_channel_list", methods=["GET", "POST"])
def get_channel_list():
    userID = get_userID_if_loggedin(request)
    print("UserID = ", userID)

    if userID is not False:
        db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30)
        cursor = db.cursor()
        res = cursor.execute("""SELECT * FROM `IRC_servers` WHERE `Registred_users_userID` = %s;""", (userID,))
        if res != 0:
            result = cursor.fetchall()
            db.close()
            print("RESULT", result)
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
                                    "useSSL": res[9]}
                servers[i] = server_dict_temp
                i = i+1

            response = {"status": "ok", "reason": "listing_servers", "message": servers}
            return jsonify(response)

        else:
            return error("ok", "no_servers_to_list", "No servers yet.")
    else:
        return error("error", "not_loggedin", "You are not logged in.")


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0") # TODO: remove binding on all interfaces; this is only here for debugging


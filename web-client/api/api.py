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

from flask import Flask, request, jsonify, redirect
app = Flask(__name__)


from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException

def is_email_valid(email_to_check): # TODO: maybe move to api_utils or sth??????
    regexp = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    result = re.match(regexp, email_to_check)
    if result is None:
        return False
    else:
        return True

@app.after_request
def after_request(response):
  response.headers.add('Access-Control-Allow-Origin', '*')
  response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Cookies')
  response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
  return response

def error(_status, _reason, _message):
    return jsonify(status=_status, reason=_reason, message=_message)

@app.route("/")
def hello_world():
    asdf = dict(status="ok", message="API is up.")
    return jsonify(asdf)

@app.route("/get_messages")
def get_messages():
    return "get_messages()"

@app.route("/login", methods=["POST"])
def login():
    _email = request.form.get("email_login") # WARNING: make lower() because USER@EXAMPLE.COM is the same as UsER@eXamPle.com !!!!!
    _password = request.form.get("password_login")
    _email = str(_email).lower()
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
                    print("At this point, we are already logged in. TODO: Redirect the user here!!!!")
                    return error("You are already logged in.", "already_loggedin", "")

            print("Reached the end of checking the session cookie with the one in DB.",
                  "The current cookie session does not exist. Gonna relog now.")

        # remove any original session we had (stupid, but whatever, I'd rather pass my last year of high school than have a good session system
        cursor = db.cursor()
        result_code = cursor.execute("DELETE FROM `User_sessions` WHERE `Registred_users_userID` = %s", (_id,))
        db.commit()

        generated_sessionID = str("testicek") # TODO: Fix
        print(generated_sessionID)

        result_code = cursor.execute("""INSERT INTO `User_sessions` (session_id, Registred_users_userID) values (%s, %s)""", (generated_sessionID, _id), )
        db.commit()

        if result_code is not 0:
            return jsonify(status="ok", message="Logged in successfully.", cookie="ok", sessionid=generated_sessionID)
        else:
            return error("An error occurred while trying to log you in.")

    elif result_code is 0:
        return error("The login information you have provided is incorrect. Check your email address and password and try again.", db)

    return jsonify(status="error", message="REACHED END OF LOGIN() WITHOUT RETURNING BEFORE THAT, THIS SHOULD NEVER HAPPEN.")


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

    if _email == is_email_valid(_email) == False: # checking for email's validness automatically already checks if it's empty
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


@app.route("/get_servers", methods=["GET", "POST"])
def get_servers():
    db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30)
    cursor = db.cursor()
    cursor.execute("SHOW TABLES;")

    tables = cursor.fetchall()

    return "get_servers();" + str(tables) + str(request.args.get("lol"))

if __name__ == '__main__':
    app.run(debug=True)
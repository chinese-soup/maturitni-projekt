#!/usr/bin/env python3
# coding=utf-8
# neumim programovat

# db
import MySQLdb

# passlib for password hashing
from passlib.hash import sha512_crypt

# randomness for session IDs
from os import urandom


from flask import Flask, request, jsonify
app = Flask(__name__)

from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException


def error(error, db_pointer):
    db_pointer.close()
    return jsonify(status="error", message=str(error))

@app.after_request
def cross_site_requests_enable(resp): # USED FOR DEBUGGING AS THE SERVER LISTENS ON :5000
    resp.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
    return resp

@app.route("/")
def hello_world():
    asdf = dict(status="ok", message="API is up.")
    return jsonify(asdf)

@app.route("/get_messages")
def get_messages():
    return "get_messages()"

@app.route("/login", methods=["POST"])
def login():
    _email = request.form.get("email") # WARNING: make lower() because USER@EXAMPLE.COM is the same as UsER@eXamPle.com !!!!!
    _password = request.form.get("password")
    _email = str(_email).lower()
    _hashed_password = sha512_crypt.encrypt(_password, salt="CodedSaltIsBad")

    db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30)

    cursor = db.cursor()
    result_code = cursor.execute("""SELECT * FROM `Registered_users` WHERE `email` = %s AND `password` = %s""", (_email, _hashed_password))

    if result_code is not 0: # use is not for extra speed (not like it matters, all code around here is slow anyway)
        values = cursor.fetchone()
        _id = values[0]
        _email = values[1]

        if "sessionid" in request.cookies:
            cookies_sessionid = request.cookies.get("sessionid")
            result_code = cursor.execute("""SELECT * FROM `User_sessions` WHERE `Registred_users_userID` = %s""", (_id,))
            if result_code is not 0:
                session_id = cursor.fetchone()
                if session_id == request.cookies["sessionid"]:
                    print("At this point, we are already logged in. Redirect the user here.")
                    return error("You are already logged in.", db)


        else:

            return jsonify(status="ok", message=str(values))

    elif result_code is 0:
        return error("The login information you have provided is incorrect.", db)

    return jsonify(status="error", message="REACHED END OF LOGIN() WITHOUT RETURNING BEFORE THAT")


@app.route("/register", methods=["GET", "POST"])
def register():
    db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30)
    try:
        _email = request.args.get("email") # WARNING: make lower() because USER@EXAMPLE.COM is the same as UsER@eXamPle.com !!!!!
        _password = request.args.get("password")
        _email = str(_email).lower()
        _hashed_password = sha512_crypt.encrypt(_password, salt="CodedSaltIsBad")
        print("EMAIL =", _email)
        print("PASSWORD =", _password)
        print("PASSWORD =", _hashed_password)

        cursor = db.cursor()
        cursor.execute("""SELECT (email) FROM `Registered_users` WHERE `email` = %s;""", (_email,))
        exists = db.affected_rows()

        if exists is not 0:
            db.close()
            return error("A user with that email is already registered. Login!", db)
        elif exists is 0:
            a = cursor.execute("""INSERT INTO `Registered_users` (email, password, isActivated) values (%s, %s, %s);""", (_email, _hashed_password, 1),)
            db.commit()
            if a == 1:
                return jsonify(status="ok", message="Your account was sucessfully registered. You can now login.")
            else:
                return error("Uknown error occurred, please try again later.", db)
        else:
            return "Error"
    except Exception as exp:
        return error(exp)
    finally:
        db.close()

@app.route("/get_servers", methods=["GET", "POST"])
def get_servers():
    db=MySQLdb.connect(user="root", passwd="asdf", db="cloudchatdb", connect_timeout=30)
    cursor = db.cursor()
    cursor.execute("SHOW TABLES;")

    tables = cursor.fetchall()

    return "get_servers();" + str(tables) + str(request.args.get("lol"))

if __name__ == '__main__':
    app.run(debug=True)
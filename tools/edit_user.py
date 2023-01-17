#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import hashlib
import sqlite3
import re
import os

current_path = os.path.dirname(os.path.realpath(__file__))
database_file = os.path.join(current_path, "..", "sql_app.db")


def hash_password(plain_text_password):
    return hashlib.sha256(plain_text_password.encode()).hexdigest()


def get_user_from_db(username=None):
    if username is None:
        sql_query = "SELECT * FROM users"
    else:
        sql_query = f"SELECT * FROM users WHERE username = '{username}'"

    con = sqlite3.connect(database_file)
    cur = con.cursor()
    cur.execute(sql_query)
    data = cur.fetchall()
    con.close()

    return data


def delete_user(username):
    con = sqlite3.connect(database_file)
    cur = con.cursor()
    cur.execute(f"DELETE FROM users WHERE username = '{username}'")
    con.commit()
    con.close()


def write_new_user(username, password, email):
    con = sqlite3.connect(database_file)
    cur = con.cursor()
    cur.execute(
        "INSERT INTO users(username, hashed_password, email, is_active, token, token_expire_time) VALUES (?, ?, ?, ?, ?, ?)",
        (username, hash_password(password), email, True, 0, 0)
    )
    con.commit()
    con.close()


def modify_user(username, password=None, email=None):

    if password is not None:
        hashed_password = hash_password(password)
        sql_query = f"UPDATE users SET hashed_password = '{hashed_password}' WHERE username = '{username}'"
    elif email is not None:
        sql_query = f"UPDATE users SET email = '{email}' WHERE username = '{username}'"
    else:
        sql_query = None

    if sql_query is not None:
        con = sqlite3.connect(database_file)
        cur = con.cursor()
        cur.execute(sql_query)
        con.commit()
        con.close()

        return True
    else:
        return False


def list_users(username=None):
    users = get_user_from_db(username=args.username)
    if len(users) == 0:
        message = "INFO: No users found in database"
        if username is not None:
            message += f" with username: {username}."
        else:
            message += "."

        print(message)
    else:
        message = "INFO: Listing users in database"
        if username is not None:
            message += f" with username: {username}"
        message += ":"

        print(message)
        for user in users:
            print("\t", user)


def validate_email(email):
    # Check if e-mail is valid
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if not re.fullmatch(regex, args.email):
        sys.exit(f"ERROR: Invalid e-mail: {email}")


def validate_password(password):
    if " " in args.password:
        sys.exit("ERROR: Password can not contain spaces.")
    if len(args.password) < 5:
        sys.exit("ERROR: Password can not be shorter than 5 characters.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--username", help="Username", required=False)
    parser.add_argument("-p", "--password", help="Password", required=False)
    parser.add_argument("-e", "--email", help="E-mail", required=False)
    parser.add_argument("-o", "--operation", help="Operation", required=True,
                        choices=['add', 'delete', 'modify', 'list'])

    args = parser.parse_args()

    if not os.path.isfile(database_file):
        sys.exit("ERROR: Database file not found. Please run the web app once first to create the database.")

    if args.operation == 'list':
        list_users()

    elif args.operation == 'add':
        if not args.password or not args.email or not args.username:
            sys.exit("ERROR: Please provide all parameters to create a new user (username, password and email)")

        # Check if user with same username exists
        users = get_user_from_db(username=args.username)
        if len(users) > 0:
            sys.exit(f"ERROR: User exists: {users[0]}")

        validate_email(args.email)

        validate_password(args.password)

        print(
            f"INFO: Creating a new username: "
            f"\n\tusername: {args.username}"
            f"\n\tpassword: {args.password}"
            f"\n\temail:    {args.email}"
            )
        write_new_user(username=args.username, email=args.email, password=args.password)
        list_users(username=args.username)

    elif args.operation == 'delete':
        if not args.username:
            sys.exit("ERROR: Please provide username of the user to delete.")

        users = get_user_from_db(username=args.username)
        if len(users) > 0:
            print(f"INFO: Deleting user with username: {args.username}")
            delete_user(args.username)
        list_users(username=args.username)

    elif args.operation == 'modify':
        if not args.username:
            sys.exit("ERROR: Please provide username of the user to modify.")

        if not args.password and not args.email:
            sys.exit("ERROR: Please provide either password or e-mail to modify.")

        if args.password and args.email:
            sys.exit("ERROR: Only one parameter can be modified, either password or e-mail.")

        if args.password:
            validate_password(args.password)
        elif args.email:
            validate_email(args.email)

        print(f"INFO: Modifying user: {args.username}")
        modify_user(username=args.username, password=args.password, email=args.email)

        list_users(username=args.username)

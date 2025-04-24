#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
import database
import helper


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--add", help="Add user", required=False)
    parser.add_argument("-d", "--delete", help="Delete user", required=False)

    database.init_db()
    helper.load_language()
    args = parser.parse_args()

    if args.add:
        if not helper.is_valid_email(args.add):
            sys.exit(f"ERROR: Invalid email{args.add}")

        database.add_user(email=args.add)

    elif args.delete:
        if not helper.is_valid_email(args.delete):
            sys.exit(f"ERROR: Invalid email{args.delete}")

        response = input(f"Deleting user: {args.delete}. Do you want to continue? (N/y):").strip().lower()

        if response in ["y", "yes"]:
            print("Deleting...")
            database.delete_user(args.delete)

    # Finally list all users to preview result.
    users = database.get_all_users()

    if len(users) == 0:
        print("No users in the database yet.")
    else:
        print("List of users:")
        for user in users:
            print(user)

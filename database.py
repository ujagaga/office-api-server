import config
import sqlite3
import time
from enum import Enum
import json

class Status(Enum):
    PENDING = "pending"
    ACTIVE = "active"


def init_db():
    try:
        with sqlite3.connect(config.DB_FILE) as conn:
            cursor = conn.cursor()

            create_users_table_sql_query = """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT,
                    status TEXT NOT NULL,
                    resolution TEXT,
                    device TEXT,
                    token TEXT,                   
                    timestamp INTEGER
                )
            """
            cursor.execute(create_users_table_sql_query)
            conn.commit()

            create_lang_table_sql_query = """
                CREATE TABLE IF NOT EXISTS language (
                    lang_id TEXT UNIQUE NOT NULL,
                    words TEXT
                )
            """
            cursor.execute(create_lang_table_sql_query)
            conn.commit()
    except sqlite3.Error as e:
        print(f"Error: {e}")


def get_language(language_id):
    sql_query = "SELECT words FROM language WHERE lang_id = ?"

    with sqlite3.connect(config.DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute(sql_query, (language_id,))

        row = cursor.fetchone()
        return json.loads(row["words"]) if row else {}


def update_language(language_id, words):
    with sqlite3.connect(config.DB_FILE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO language (lang_id, words) VALUES (?, ?)",
                (language_id, words),
            )
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error: {e}")


def get_language_list():
    sql_query = "SELECT lang_id FROM language"

    with sqlite3.connect(config.DB_FILE) as conn:
        conn.row_factory = sqlite3.Row  # Enables dictionary-like row access
        cursor = conn.cursor()
        cursor.execute(sql_query)
        data = cursor.fetchall()
        lang_list = [dict(row)['lang_id'] for row in data]

        return lang_list

def get_user_by_email(email):
    sql_query = "SELECT * FROM users WHERE email = ?"
    params = (email, )

    with sqlite3.connect(config.DB_FILE) as conn:
        conn.row_factory = sqlite3.Row  # Enables dictionary-like row access
        cursor = conn.cursor()
        cursor.execute(sql_query, params)

        data = cursor.fetchone()
        user = dict(data) if data else None  # Convert row to dict if found
        return user


def get_user_by_token(token, status=None):
    if not status:
        sql_query = "SELECT * FROM users WHERE token = ?"
        params = (token, )
    else:
        sql_query = "SELECT * FROM users WHERE token = ? AND status != ?"
        params = (token, Status.PENDING.value)


    with sqlite3.connect(config.DB_FILE) as conn:
        conn.row_factory = sqlite3.Row  # Enables dictionary-like row access
        cursor = conn.cursor()
        cursor.execute(sql_query, params)

        data = cursor.fetchone()
        user = dict(data) if data else None  # Convert row to dict if found
        return user


def get_all_users():
    sql_query = "SELECT * FROM users"

    with sqlite3.connect(config.DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql_query)

        data = cursor.fetchall()
        return [dict(row) for row in data]


def get_pending_user_count():
    sql_query = "SELECT COUNT(*) FROM users WHERE status = ?"

    try:
        with sqlite3.connect(config.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_query, (Status.PENDING.value,))
            count = cursor.fetchone()[0]  # Get the count directly
            return count
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return 0  # Return 0 if there's an error


def user_exists(user_id):
    sql_query = "SELECT 1 FROM users WHERE id = ? LIMIT 1"
    params = (user_id,)

    try:
        with sqlite3.connect(config.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_query, params)
            return cursor.fetchone() is not None  # Returns True if user exists
    except sqlite3.Error as e:
        print("Database error:", e)
        return False


def add_user(email):
    timestamp = int(time.time())
    with sqlite3.connect(config.DB_FILE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (email, status, timestamp) VALUES (?, ?, ?)",
                (email, Status.PENDING.value, timestamp),
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            pass

    return False


def delete_user(email):
    try:
        with sqlite3.connect(config.DB_FILE) as conn:
            cursor = conn.cursor()

            # Use parameterized query to prevent SQL injection
            cursor.execute("DELETE FROM users WHERE email = ?", (email,))
            conn.commit()

            if cursor.rowcount > 0:
                print(f"User with email {email} deleted.")
            else:
                print(f"No user found with email {email}.")

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"Exception: {e}")


def update_user(email, status=None, token=None, password=None, resolution=None, device=None):
    timestamp = int(time.time())
    updates = []

    # Collect the set of updates based on the provided arguments
    if status is not None:
        updates.append(("status", status))
    if password is not None:
        updates.append(("password", password))
    if resolution is not None:
        updates.append(("resolution", resolution))
    if device is not None:
        updates.append(("device", device))
    if token is not None:
        updates.append(("token", token))
        updates.append(("timestamp", timestamp))  # Update timestamp when token is updated

    # If no updates are provided, return False
    if not updates:
        return False

    # Construct the SET clause for the SQL query
    set_clause = ", ".join([f"{column} = ?" for column, _ in updates])
    values = [value for _, value in updates]

    # Prepare the SQL query
    sql_query = f"UPDATE users SET {set_clause} WHERE email = ?"
    values.append(email)  # Add email as the last parameter (for WHERE clause)

    try:
        with sqlite3.connect(config.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute(sql_query, values)  # Execute with parameters to prevent SQL injection
            conn.commit()

        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

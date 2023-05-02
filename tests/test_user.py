import datetime
import os
import sqlite3
import unittest
from unittest.mock import MagicMock, patch


class TestGetOrCreateUser(unittest.TestCase):

    def setUp(self):
        # Set up mock objects for the bot and message
        self.bot = MagicMock()
        self.message = MagicMock()
        self.message.from_user.id = 123456789
        self.message.from_user.username = "testuser"

    def setup_db(self):
        if os.environ.get("test_database.db") is not None:
            os.remove("test_database.db")
        self.conn = sqlite3.connect("test_database.db")
        self.c = self.conn.cursor()

        # Create the "users" table if not already created
        columns = [
            "id INTEGER PRIMARY KEY",
            "username TEXT",
            "email TEXT NULL",
            "phone TEXT NULL",
            "num_requests INTEGER DEFAULT 0",
            "balance REAL DEFAULT 0.0",
            "date_paid DATE",
            "amount_due REAL DEFAULT 0.0",
            "expiry_time TIMESTAMP",
            "start_date TIMESTAMP"
        ]

        query = f"CREATE TABLE IF NOT EXISTS users ({', '.join(columns)})"
        self.c.execute(query)
        self.conn.commit()
        self.conn.close()

    def tear_down_db(self):
        os.remove("test_database.db")

    def get_connection(self):
        # Connect to the database and return the connection
        return sqlite3.connect("test_database.db")

    @patch.dict(os.environ, {"DB_NAME": "test_database.db"})
    def test_get_or_create_user_new_user(self):
        from user import get_or_create_user

        self.setup_db()
        # Call the function with the message object
        result = get_or_create_user(self.message)

        # Check that the function returns True
        self.assertEqual(result, True)

        # Check that the user was added to the database
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE id = ?",
                  (self.message.from_user.id,))
        result = c.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[0], self.message.from_user.id)
        self.assertEqual(result[1], self.message.from_user.username)
        conn.close()
        self.tear_down_db()

    @patch.dict(os.environ, {"DB_NAME": "test_database.db"})
    def test_get_or_create_user_existing_user(self):
        from user import get_or_create_user

        self.setup_db()
        conn = self.get_connection()
        c = conn.cursor()
        # Add a user to the "users" table in the database
        c.execute("INSERT INTO users (id, username) VALUES (?, ?)",
                  (self.message.from_user.id, self.message.from_user.username))
        conn.commit()
        conn.close()

        # Call the function with the message object
        result = get_or_create_user(self.message)

        # Check that the function returns True
        self.assertEqual(result, True)

        conn = self.get_connection()
        c = conn.cursor()
        # Check that the user was not added again to the database
        c.execute("SELECT * FROM users WHERE id = ?",
                  (self.message.from_user.id,))
        result = c.fetchall()
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        conn.close()
        self.tear_down_db()

    @patch.dict(os.environ, {"DB_NAME": "test_database.db"})
    def test_existing_user_requests(self):
        from user import increment_requests

        self.setup_db()
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("select * from users")
        print(c.fetchone())
        # # Add a user to the "users" table in the database
        c.execute("INSERT INTO users (id, username) VALUES (?, ?)",
                  (self.message.from_user.id, self.message.from_user.username))
        conn.commit()
        conn.close()

        increment_requests(self.message)

        conn = self.get_connection()
        c = conn.cursor()
        result = c.execute("SELECT num_requests FROM users WHERE id = ?",
                           (self.message.from_user.id,)).fetchone()
        self.assertEqual(result[0], 1)
        self.tear_down_db()

    @patch.dict(os.environ, {"DB_NAME": "test_database.db"})
    def test_not_expired(self):
        from user import check_expired_account

        self.setup_db()
        conn = self.get_connection()
        c = conn.cursor()
        # Add a user to the "users" table in the database
        # user expires 30 days from now
        expiry_date = datetime.datetime.now() + datetime.timedelta(days=30)
        c.execute(
            "INSERT INTO users (id, username, expiry_time) VALUES (?, ?, ?)",
            (self.message.from_user.id,
             self.message.from_user.username,
             expiry_date))
        conn.commit()
        conn.close()

        self.assertEqual(check_expired_account(self.message), False)
        self.tear_down_db()

    @patch.dict(os.environ, {"DB_NAME": "test_database.db"})
    def test_expired(self):
        from user import check_expired_account

        self.setup_db()
        conn = self.get_connection()
        c = conn.cursor()
        # Add a user to the "users" table in the database
        expiry_date = datetime.datetime.now() - datetime.timedelta(days=30)
        c.execute(
            "INSERT INTO users (id, username, expiry_time) VALUES (?, ?, ?)",
            (self.message.from_user.id,
             self.message.from_user.username,
             expiry_date))
        conn.commit()
        conn.close()
        self.assertEqual(check_expired_account(self.message), True)
        self.tear_down_db()

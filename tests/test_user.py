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
        # Drop the "users" table
        self.conn = sqlite3.connect("test_database.db")
        self.c = self.conn.cursor()
        self.c.execute("DROP TABLE users")
        self.conn.commit()
        self.conn.close()

    def get_connection(self):
        # Connect to the database and return the connection
        return sqlite3.connect("test_database.db")

    @patch.dict(os.environ, {"DB_NAME": "test_database.db"})
    @patch('src.controllers.user.bot.send_message')
    def test_get_or_create_user_new_user(self, mock_bot_send_message):
        from src.controllers.user import get_or_create_user

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
        mock_bot_send_message.assert_called_once()
        conn.close()
        self.tear_down_db()

    @patch.dict(os.environ, {"DB_NAME": "test_database.db"})
    def test_get_or_create_user_existing_user(self):
        from src.controllers.user import get_or_create_user
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
        from src.controllers.user import increment_requests

        self.setup_db()
        conn = self.get_connection()
        c = conn.cursor()
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
        from src.controllers.user import check_expired_account

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
        from src.controllers.user import check_expired_account

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

    @patch.dict(os.environ, {"DB_NAME": "test_database.db"})
    @patch('src.controllers.user.bot.send_message')
    def test_existing_user_account_extended(self, mock_bot_send_message):
        from src.controllers.user import extend_account
        self.setup_db()
        conn = self.get_connection()
        c = conn.cursor()
        # # Prepare mock database response and current date
        expiry_date = datetime.datetime.now() + datetime.timedelta(days=10)
        c.execute(
            "INSERT INTO users (id, username, expiry_time) VALUES (?, ?, ?)",
            (123,
             self.message.from_user.username,
             expiry_date))
        conn.commit()

        conn.close()
        message = self.message.from_user.username + ', 7'
        # Call the function being tested
        extend_account(message)

        conn = self.get_connection()
        c = conn.cursor()
        # Check the new expiry date
        c.execute('SELECT id, expiry_time FROM users WHERE username = ?', (self.message.from_user.username, ))

        result = c.fetchone()
        self.assertIsNotNone(result)
        time = datetime.datetime.strptime(result[1], '%Y-%m-%d %H:%M:%S.%f')
        self.assertEqual(time, expiry_date + datetime.timedelta(days=7))
        self.tear_down_db()

    @patch.dict(os.environ, {"DB_NAME": "test_database.db"})
    def test_total_count_joined_users(self):
        from src.controllers.user import count_joined_users
        self.setup_db()
        conn = self.get_connection()
        c = conn.cursor()
        c.execute(
            """INSERT INTO users (id, username, start_date) VALUES 
               ('123', 'Alice', '2021-01-01'),
               ('124', 'Bob', '2021-02-01'),
               ('444', 'Charlie', '2021-03-01')"""
        )
        conn.commit()
        conn.close()
        # Call the function being tested
        result = count_joined_users()
        self.assertEqual(result, 3)
        self.tear_down_db()

    @patch.dict(os.environ, {"DB_NAME": "test_database.db"})
    def test_todays_joined_users(self):
        from src.controllers.user import count_joined_users
        self.setup_db()
        conn = self.get_connection()
        c = conn.cursor()
        today = datetime.datetime.today()
        start_of_today = datetime.datetime(today.year, today.month, today.day)
        user_start_time = start_of_today + datetime.timedelta(seconds=1)
        c.execute(
            """INSERT INTO users (id, username, start_date) VALUES 
               ('123', 'Alice', '{}'),
               ('124', 'Bob', '2021-02-01'),
               ('444', 'Charlie', '2021-03-01')""".format(user_start_time)
        )
        conn.commit()
        conn.close()
        # Call the function being tested
        result = count_joined_users(from_date=start_of_today)
        self.assertEqual(result, 1)
        self.tear_down_db()

    @patch.dict(os.environ, {"DB_NAME": "test_database.db"})
    def test_can_request(self):
        from src.controllers.user import check_in_trial
        self.setup_db()
        conn = self.get_connection()
        c = conn.cursor()
        start_time = datetime.datetime.now()
        # A user who just joined
        c.execute("""INSERT INTO users (id, username, start_date) VALUES 
               ('123', 'Alice', '{}')""".format(start_time))

        # A user who joined 30 days ago
        c.execute("""INSERT INTO users (id, username, start_date) VALUES
                ('124', 'Bob', '{}')""".format(start_time - datetime.timedelta(days=30)))

        conn.commit()
        conn.close()
        # Call the function being tested
        result = check_in_trial(123)
        self.assertEqual(result, True)

        result = check_in_trial(124)
        self.assertEqual(result, False)
        self.tear_down_db()

    @patch.dict(os.environ, {"DB_NAME": "test_database.db"})
    def test_count_requests(self):
        from src.controllers.user import count_requests
        self.setup_db()
        conn = self.get_connection()
        c = conn.cursor()
        # A user who just joined
        c.execute("""INSERT INTO users (id, username, num_requests) VALUES 
               ('123', 'Alice', 10),
               ('124', 'Bob', 100)""")
        conn.commit()
        conn.close()
        # Call the function being tested
        result = count_requests()
        self.assertEqual(result, 110)
        self.tear_down_db()

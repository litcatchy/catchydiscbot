import sqlite3
import os

class Database:
    def __init__(self, db_path="data/stats.db"):
        # ✅ Ensure the 'data' folder exists
        os.makedirs("data", exist_ok=True)

        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        """Creates tables if they don't exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                user_id INTEGER PRIMARY KEY,
                messages_sent INTEGER DEFAULT 0,
                vc_time INTEGER DEFAULT 0  -- in seconds
            )
        """)
        self.conn.commit()

    def add_message(self, user_id, guild_id=None):
        """Increases message count for a user (only counts once per 4 sec)."""
        self.cursor.execute("""
            INSERT INTO user_stats (user_id, messages_sent)
            VALUES (?, 1)
            ON CONFLICT(user_id) DO UPDATE SET messages_sent = messages_sent + 1
        """, (user_id,))
        self.conn.commit()

    def get_message_count(self, user_id, guild_id=None):
        """Gets the number of messages sent by a user."""
        self.cursor.execute("SELECT messages_sent FROM user_stats WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0  # Returns 0 if user has no data

    def update_vc_time(self, user_id, seconds):
        """Increases VC time (in seconds)."""
        self.cursor.execute("""
            INSERT INTO user_stats (user_id, vc_time)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET vc_time = vc_time + ?
        """, (user_id, seconds, seconds))
        self.conn.commit()

    def get_vc_time(self, user_id):
        """Gets the total VC time of a user."""
        self.cursor.execute("SELECT vc_time FROM user_stats WHERE user_id = ?", (user_id,))
        result = self.cursor.fetchone()
        return result[0] if result else 0  # Returns 0 if user has no data

    def get_top_chatters(self, limit=10):
        """Gets top users by message count."""
        self.cursor.execute("SELECT user_id, messages_sent FROM user_stats ORDER BY messages_sent DESC LIMIT ?", (limit,))
        return self.cursor.fetchall()

    def get_top_vc(self, limit=10):
        """Gets top users by VC time."""
        self.cursor.execute("SELECT user_id, vc_time FROM user_stats ORDER BY vc_time DESC LIMIT ?", (limit,))
        return self.cursor.fetchall()

    def close(self):
        """Closes the database connection."""
        self.conn.close()

import sqlite3
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Database:
    def __init__(self, db_path="data/stats.db"):
        # Ensure the path is absolute and consistent
        db_path = os.path.join(os.getcwd(), "data", "stats.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)  # Ensure 'data' folder exists
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()
        logging.debug(f"Database initialized at {db_path}")

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

    def update_messages(self, user_id):
        """Ensures user exists and updates message count."""
        self.cursor.execute("""
            INSERT OR IGNORE INTO user_stats (user_id, messages_sent, vc_time) 
            VALUES (?, 0, 0)
        """, (user_id,))

        self.cursor.execute("""
            UPDATE user_stats 
            SET messages_sent = messages_sent + 1 
            WHERE user_id = ?
        """, (user_id,))
        
        self.conn.commit()
        logging.debug(f"Updated messages for user {user_id}")

    def update_vc_time(self, user_id, seconds):
        """Ensures user exists and updates VC time."""
        self.cursor.execute("""
            INSERT OR IGNORE INTO user_stats (user_id, messages_sent, vc_time) 
            VALUES (?, 0, 0)
        """, (user_id,))

        self.cursor.execute("""
            UPDATE user_stats 
            SET vc_time = vc_time + ? 
            WHERE user_id = ?
        """, (seconds, user_id))
        
        self.conn.commit()
        logging.debug(f"Updated VC time for user {user_id}: {seconds} seconds")

    def get_user_stats(self, user_id):
        """Gets stats for a specific user."""
        self.cursor.execute("SELECT messages_sent, vc_time FROM user_stats WHERE user_id = ?", (user_id,))
        stats = self.cursor.fetchone() or (0, 0)  # Default if user has no data
        logging.debug(f"Fetched stats for user {user_id}: {stats}")
        return stats

    def get_top_chatters(self, limit=50):
        """Gets top 50 users by message count."""
        self.cursor.execute("SELECT user_id, messages_sent FROM user_stats ORDER BY messages_sent DESC LIMIT ?", (limit,))
        top_chatters = self.cursor.fetchall()
        logging.debug(f"Fetched top chatters: {top_chatters}")
        return top_chatters

    def get_top_vc(self, limit=50):
        """Gets top 50 users by VC time."""
        self.cursor.execute("SELECT user_id, vc_time FROM user_stats ORDER BY vc_time DESC LIMIT ?", (limit,))
        top_vc = self.cursor.fetchall()
        logging.debug(f"Fetched top VC users: {top_vc}")
        return top_vc

    def close(self):
        """Closes the database connection."""
        self.conn.close()
        logging.debug("Database connection closed.")
    
    def check_integrity(self):
        """Check the integrity of the database."""
        self.cursor.execute("PRAGMA integrity_check;")
        result = self.cursor.fetchone()
        if result[0] != 'ok':
            logging.error("Database is corrupted!")
        else:
            logging.debug("Database integrity is fine.")

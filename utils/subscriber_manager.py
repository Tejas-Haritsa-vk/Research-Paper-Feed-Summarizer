
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class SubscriberManager:
    """
    Manages subscriber data using a SQLite database.
    Schema:
        - email (TEXT PRIMARY KEY)
        - topics (TEXT - JSON)
        - joined_date (TEXT)
        - is_active (BOOLEAN)
    """

    def __init__(self, db_path: str = "subscribers.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                email TEXT PRIMARY KEY,
                topics TEXT,
                joined_date TEXT,
                is_active INTEGER DEFAULT 1
            )
        ''')
        conn.commit()
        conn.close()

    def add_subscriber(self, email: str, topics: List[str] = None):
        """Add a new subscriber or update existing one."""
        if topics is None:
            topics = ["AI", "Deep Learning"]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        joined_date = datetime.now().isoformat()
        topics_json = json.dumps(topics)
        
        try:
            cursor.execute('''
                INSERT INTO subscribers (email, topics, joined_date, is_active)
                VALUES (?, ?, ?, 1)
                ON CONFLICT(email) DO UPDATE SET
                    topics=excluded.topics,
                    is_active=1
            ''', (email, topics_json, joined_date))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding subscriber {email}: {e}")
            return False
        finally:
            conn.close()

    def remove_subscriber(self, email: str):
        """Soft delete a subscriber."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE subscribers SET is_active = 0 WHERE email = ?', (email,))
            conn.commit()
        finally:
            conn.close()

    def get_active_subscribers(self) -> List[Dict]:
        """Get all active subscribers."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        subscribers = []
        try:
            cursor.execute('SELECT * FROM subscribers WHERE is_active = 1')
            rows = cursor.fetchall()
            for row in rows:
                subscribers.append({
                    'email': row['email'],
                    'topics': json.loads(row['topics']),
                    'joined_date': row['joined_date']
                })
        finally:
            conn.close()
        
        return subscribers

    def update_topics(self, email: str, topics: List[str]):
        """Update topics for a subscriber."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            topics_json = json.dumps(topics)
            cursor.execute('UPDATE subscribers SET topics = ? WHERE email = ?', (topics_json, email))
            conn.commit()
        finally:
            conn.close()

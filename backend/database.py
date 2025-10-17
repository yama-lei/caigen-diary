"""
Database operations for the diary archive system.
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import os


class DiaryDatabase:
    def __init__(self, db_path: str = "data/diaries.db"):
        self.db_path = db_path
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_database()
    
    def get_connection(self):
        """Create a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn
    
    def init_database(self):
        """Initialize the database schema."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create diaries table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                content TEXT NOT NULL,
                sentiment VARCHAR(10),
                positive_prob REAL,
                negative_prob REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, content)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON diaries(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentiment ON diaries(sentiment)")
        
        conn.commit()
        conn.close()
        print(f"Database initialized at {self.db_path}")
    
    def insert_diary(self, date: str, content: str) -> Optional[int]:
        """
        Insert a diary entry. Returns the entry ID if successful, None if duplicate.
        
        Args:
            date: Date in YYYY-MM-DD format
            content: Diary content
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO diaries (date, content) VALUES (?, ?)",
                (date, content)
            )
            conn.commit()
            entry_id = cursor.lastrowid
            conn.close()
            return entry_id
        except sqlite3.IntegrityError:
            # Duplicate entry
            conn.close()
            return None
    
    def update_sentiment(self, entry_id: int, sentiment: str, 
                        positive_prob: float, negative_prob: float):
        """Update sentiment analysis results for an entry."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE diaries 
            SET sentiment = ?, positive_prob = ?, negative_prob = ?
            WHERE id = ?
        """, (sentiment, positive_prob, negative_prob, entry_id))
        
        conn.commit()
        conn.close()
    
    def get_entries_by_date(self, date: str) -> List[Dict]:
        """Get all entries for a specific date."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM diaries WHERE date = ? ORDER BY id",
            (date,)
        )
        
        entries = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return entries
    
    def get_entries_by_month(self, year: int, month: int) -> List[Dict]:
        """Get all entries for a specific month."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT * FROM diaries 
               WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
               ORDER BY date, id""",
            (str(year), f"{month:02d}")
        )
        
        entries = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return entries
    
    def get_entries_by_sentiment(self, sentiment: str) -> List[Dict]:
        """Get all entries with a specific sentiment."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM diaries WHERE sentiment = ? ORDER BY date, id",
            (sentiment,)
        )
        
        entries = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return entries
    
    def get_all_entries(self, limit: Optional[int] = None, 
                       offset: Optional[int] = None) -> List[Dict]:
        """Get all diary entries with optional pagination."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM diaries ORDER BY date DESC, id DESC"
        if limit is not None:
            query += f" LIMIT {limit}"
            if offset is not None:
                query += f" OFFSET {offset}"
        
        cursor.execute(query)
        entries = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return entries
    
    def get_entries_without_sentiment(self) -> List[Dict]:
        """Get all entries that don't have sentiment analysis yet."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM diaries WHERE sentiment IS NULL ORDER BY id"
        )
        
        entries = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return entries
    
    def get_statistics(self) -> Dict:
        """Get overall statistics about the diary entries."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total count
        cursor.execute("SELECT COUNT(*) as total FROM diaries")
        total = cursor.fetchone()["total"]
        
        # Sentiment distribution
        cursor.execute("""
            SELECT sentiment, COUNT(*) as count 
            FROM diaries 
            WHERE sentiment IS NOT NULL
            GROUP BY sentiment
        """)
        sentiment_dist = {row["sentiment"]: row["count"] for row in cursor.fetchall()}
        
        # Date range
        cursor.execute("SELECT MIN(date) as first_date, MAX(date) as last_date FROM diaries")
        date_range = dict(cursor.fetchone())
        
        # Entries per month
        cursor.execute("""
            SELECT strftime('%Y-%m', date) as month, COUNT(*) as count
            FROM diaries
            GROUP BY month
            ORDER BY month
        """)
        monthly_counts = {row["month"]: row["count"] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "total": total,
            "sentiment_distribution": sentiment_dist,
            "date_range": date_range,
            "monthly_counts": monthly_counts
        }


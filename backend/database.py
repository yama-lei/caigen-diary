"""
Database operations for the diary archive system.
Simplified version without sentiment analysis.
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
        
        # Create diaries table (simplified, no sentiment fields)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS diaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date, content)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON diaries(date)")
        
        conn.commit()
        conn.close()
        print(f"Database initialized at {self.db_path}")
    
    def insert_diary(self, date: str, content: str) -> Optional[int]:
        """
        Insert a diary entry. Returns the entry ID if successful, None if duplicate.
        
        Args:
            date: Date in YYYY-MM-DD format
            content: Diary content
            
        Returns:
            Entry ID if successful, None if duplicate
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
    
    def insert_many(self, entries: List[Dict[str, str]]) -> Dict:
        """
        Insert multiple diary entries.
        
        Args:
            entries: List of dicts with 'date' and 'content' keys
            
        Returns:
            Dict with counts: total, success, duplicate, failed
        """
        total = len(entries)
        success = 0
        duplicate = 0
        failed = 0
        details = []
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for entry in entries:
            try:
                date = entry.get('date')
                content = entry.get('content')
                
                if not date or not content:
                    failed += 1
                    details.append({
                        "date": date,
                        "content": content[:50] if content else "",
                        "status": "failed",
                        "reason": "缺少必要字段"
                    })
                    continue
                
                cursor.execute(
                    "INSERT INTO diaries (date, content) VALUES (?, ?)",
                    (date, content)
                )
                conn.commit()
                success += 1
                details.append({
                    "date": date,
                    "content": content[:50],
                    "status": "success"
                })
            except sqlite3.IntegrityError:
                # Duplicate entry
                duplicate += 1
                details.append({
                    "date": entry.get('date'),
                    "content": entry.get('content', '')[:50],
                    "status": "duplicate",
                    "reason": "重复条目"
                })
            except Exception as e:
                failed += 1
                details.append({
                    "date": entry.get('date'),
                    "content": entry.get('content', '')[:50],
                    "status": "failed",
                    "reason": str(e)
                })
        
        conn.close()
        
        return {
            "total": total,
            "success": success,
            "duplicate": duplicate,
            "failed": failed,
            "details": details
        }
    
    def get_entry_by_id(self, entry_id: int) -> Optional[Dict]:
        """Get a single entry by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM diaries WHERE id = ?", (entry_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
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
    
    def search_entries(self, query: str, limit: int = 50) -> List[Dict]:
        """Search entries by content."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM diaries
            WHERE content LIKE ?
            ORDER BY date DESC
            LIMIT ?
        """, (f"%{query}%", limit))
        
        entries = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return entries
    
    def update_entry(self, entry_id: int, date: Optional[str] = None, 
                    content: Optional[str] = None) -> bool:
        """Update a diary entry."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if entry exists
        cursor.execute("SELECT id FROM diaries WHERE id = ?", (entry_id,))
        if not cursor.fetchone():
            conn.close()
            return False
        
        # Build update query
        update_fields = []
        params = []
        
        if date is not None:
            update_fields.append("date = ?")
            params.append(date)
        
        if content is not None:
            update_fields.append("content = ?")
            params.append(content)
        
        if not update_fields:
            conn.close()
            return False
        
        params.append(entry_id)
        query = f"UPDATE diaries SET {', '.join(update_fields)} WHERE id = ?"
        
        try:
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Duplicate entry after update
            conn.close()
            return False
    
    def delete_entry(self, entry_id: int) -> bool:
        """Delete a diary entry."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM diaries WHERE id = ?", (entry_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        return deleted
    
    def get_statistics(self) -> Dict:
        """Get overall statistics about the diary entries."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total count
        cursor.execute("SELECT COUNT(*) as total FROM diaries")
        total = cursor.fetchone()["total"]
        
        # Date range
        cursor.execute("SELECT MIN(date) as first_date, MAX(date) as last_date FROM diaries")
        date_range = dict(cursor.fetchone())
        
        # Entries per month
        cursor.execute("""
            SELECT strftime('%Y-%m', date) as month, COUNT(*) as count
            FROM diaries
            GROUP BY month
            ORDER BY month DESC
        """)
        monthly_counts = {row["month"]: row["count"] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "total": total,
            "date_range": date_range,
            "monthly_counts": monthly_counts
        }

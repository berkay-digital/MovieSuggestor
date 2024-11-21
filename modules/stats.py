import sqlite3
from datetime import datetime
import os


class StatsTracker:
    def __init__(self):
        self.db_path = 'stats.db'
        self._init_db()

    def _init_db(self):
        # Create database directory if it doesn't exist
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create the searches table if it doesn't exist
        c.execute('''CREATE TABLE IF NOT EXISTS searches
                    (title TEXT, 
                     media_type TEXT, 
                     count INTEGER DEFAULT 0, 
                     first_searched TIMESTAMP,
                     last_searched TIMESTAMP)''')
        
        # Add any indexes if needed
        c.execute('''CREATE INDEX IF NOT EXISTS idx_title_media 
                    ON searches(title, media_type)''')
        
        conn.commit()
        conn.close()

    def _ensure_table_exists(self):
        """Ensure the searches table exists before any operation"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Check if table exists
        c.execute('''SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='searches' ''')
        
        if not c.fetchone():
            self._init_db()
        
        conn.close()

    def get_total_unique_titles(self):
        self._ensure_table_exists()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT COUNT(DISTINCT title) FROM searches')
        count = c.fetchone()[0] or 0
        conn.close()
        return count

    def get_total_searches(self):
        self._ensure_table_exists()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT SUM(count) FROM searches')
        count = c.fetchone()[0] or 0
        conn.close()
        return count

    def get_movie_titles(self):
        self._ensure_table_exists()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM searches WHERE media_type = "movie"')
        count = c.fetchone()[0] or 0
        conn.close()
        return count

    def get_tv_show_titles(self):
        self._ensure_table_exists()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM searches WHERE media_type = "tv"')
        count = c.fetchone()[0] or 0
        conn.close()
        return count

    def get_top_searches(self, limit=10):
        self._ensure_table_exists()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''SELECT title, media_type, count, first_searched, last_searched 
                    FROM searches ORDER BY count DESC LIMIT ?''', (limit,))
        results = c.fetchall() or []
        conn.close()
        return results

    def get_recent_searches(self, limit=10):
        self._ensure_table_exists()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''SELECT title, media_type, count, first_searched, last_searched 
                    FROM searches ORDER BY last_searched DESC LIMIT ?''', (limit,))
        results = c.fetchall() or []
        conn.close()
        return results

    def track_search(self, title, media_type):
        self._ensure_table_exists()
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            # Check if title exists
            c.execute('SELECT * FROM searches WHERE title = ? AND media_type = ?', 
                     (title, media_type))
            result = c.fetchone()
            
            if result:
                # Update existing record
                c.execute('''UPDATE searches 
                            SET count = count + 1, last_searched = ? 
                            WHERE title = ? AND media_type = ?''', 
                         (now, title, media_type))
            else:
                # Insert new record
                c.execute('''INSERT INTO searches 
                            (title, media_type, count, first_searched, last_searched)
                            VALUES (?, ?, 1, ?, ?)''', 
                         (title, media_type, now, now))
            
            conn.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()
        finally:
            conn.close()


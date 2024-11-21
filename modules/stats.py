import sqlite3
from datetime import datetime
from contextlib import contextmanager


class StatsTracker:
    def __init__(self, db_path="stats.db"):
        self.db_path = db_path
        self.__init__()

    @contextmanager
    def get_db(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def _init_db(self):
        with self.get_db() as conn:
            cursor = conn.cursor()

            # Create searches table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS searches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    media_type TEXT NOT NULL,
                    search_count INTEGER DEFAULT 1,
                    first_searched TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_searched TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create index on title and media_type
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_title_media_type 
                ON searches(title, media_type)
            ''')

            conn.commit()

    def track_search(self, title: str, media_type: str):
        with self.get_db() as conn:
            cursor = conn.cursor()

            # Try to update existing record
            cursor.execute('''
                UPDATE searches 
                SET search_count = search_count + 1,
                    last_searched = CURRENT_TIMESTAMP
                WHERE title = ? AND media_type = ?
            ''', (title, media_type))

            # If no record was updates, insert new one
            if cursor.rowcount == 0:
                cursor.execute('''
                INSERT INTO searches (title, media_type)
                VALUES (?, ?)
                ''', (title, media_type))

            conn.commit()

    def get_top_searches(self, limit: int = 10, media_type: str = None):
        with self.get_db() as conn:
            cursor = conn.cursor()

            if media_type:
                cursor.execute('''
                    SELECT title, media_type, search_count, first_searched, last_searched
                    FROM searches
                    WHERE media_type = ?
                    ORDER BY search_count DESC
                    LIMIT ?
                ''', (media_type, limit))

            else:
                cursor.execute('''
                    SELECT title, media_type, search_count, first_searched, last_searched
                    FROM searches
                    ORDER BY search_count DESC
                    LIMIT ?
                ''', (limit,))

            return cursor.fetchall()

    def get_total_searches(self):
        with self.get_db() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT
                    COUNT(*) as total_titles,
                    SUM(search_count) as total_searches,
                    COUNT(CASE WHEN media_type = 'movie' THEN 1 END) as movie_titles,
                    COUNT(CASE WHEN media_type = 'tv' THEN 1 END) as tv_titles,
                    SUM(CASE WHEN media_type = 'movie' THEN search_count END) as movie_searches,
                    SUM(CASE WHEN media_type = 'tv' THEN search_count END) as tv_searches
                FROM searches
            ''')

            return cursor.fetchall()

    def get_recent_searches(self, limit: int = 10):
        with self.get_db() as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT title, media_type, search_count, first_searched, last_searched
                FROM searches
                ORDER BY last_searched DESC
                LIMIT ?
            ''', (limit,))

            return cursor.fetchall()


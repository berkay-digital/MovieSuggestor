import sqlite3
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
            conn.clone()

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
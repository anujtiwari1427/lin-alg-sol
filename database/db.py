import sqlite3
import os


def get_db_connection(db_path=None):
    """
    Create and return a SQLite database connection.
    
    Args:
        db_path: Optional path to database. Defaults to the path from Config.
                 Pass ':memory:' for in-memory test databases.
    """
    if db_path is None:
        # Lazy import to avoid circular import issues
        from config import Config
        db_path = Config.DATABASE_PATH

    # Only create directories for real file paths, not ':memory:'
    if db_path != ':memory:':
        try:
            dir_path = os.path.dirname(db_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)

            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            # Enable WAL mode for better concurrent access on file DBs
            try:
                conn.execute('PRAGMA journal_mode=WAL;')
            except sqlite3.OperationalError:
                pass
            return conn
        except Exception:
            # Fallback to /tmp if current directory is read-only (e.g., Vercel / AWS Lambda)
            tmp_db_path = '/tmp/app.db'
            conn = sqlite3.connect(tmp_db_path)
            conn.row_factory = sqlite3.Row
            return conn

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=None):
    """
    Initialize database tables.
    
    Args:
        db_path: Optional path override. Defaults to Config.DATABASE_PATH.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Calculation history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS calculation_history (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            module       TEXT NOT NULL,
            operation    TEXT NOT NULL,
            input_data   TEXT NOT NULL,
            result_data  TEXT NOT NULL,
            steps_json   TEXT,
            is_favourite INTEGER DEFAULT 0,
            export_count INTEGER DEFAULT 0,
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Safe migration for existing DB files
    cursor.execute("PRAGMA table_info(calculation_history)")
    columns = [col['name'] for col in cursor.fetchall()]
    if 'is_favourite' not in columns:
        cursor.execute("ALTER TABLE calculation_history ADD COLUMN is_favourite INTEGER DEFAULT 0")
    if 'export_count' not in columns:
        cursor.execute("ALTER TABLE calculation_history ADD COLUMN export_count INTEGER DEFAULT 0")

    # User settings / preferences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

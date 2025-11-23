import sqlite3
from pathlib import Path

DB_NAME = Path(__file__).resolve().parent / "call_analyzer.db"

def get_db_connection():
    """
    Returns a connection to the SQLite database.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Note for self: Enables dictionary-like access to rows
    return conn

def initialize_db():
    """
    Initializes the SQLite database and creates the 'call_analyses' table.
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS call_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            full_transcript TEXT,
            summary TEXT,
            tags TEXT,
            language TEXT,
            transcribe_time REAL,
            analysis_time REAL,
            processed_where TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        print(f"Database initialized at: {DB_NAME}")
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    initialize_db()
    print("DB initialization complete.")
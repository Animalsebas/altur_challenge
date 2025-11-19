import sqlite3
import os

DB_NAME = "call_analyzer.db"

def initialize_db():
    """
    Initializes the SQLite database and creates the 'call_analyses' table.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        print(f"Database connection successful. File: {os.path.abspath(DB_NAME)}")

        create_table_query = """
        CREATE TABLE IF NOT EXISTS call_analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL UNIQUE,
            full_transcript TEXT,
            summary TEXT,
            tags TEXT,
            sentiment TEXT,
            language TEXT NOT NULL,
            uploaded_at TIMESTAMP,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        print("Table 'call_analyses' created or already exists.")
        
    except sqlite3.Error as e:
        print(f"An error occurred during database initialization: {e}")
        
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    initialize_db()
    print("\nInitialization finished.")
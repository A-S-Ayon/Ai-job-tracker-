import sqlite3
from datetime import datetime

DB_PATH = "jobs.db"

def get_connection():
    """Context-managed connection for safe DB operations."""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initializes the database schema."""
    query = """
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        job_url TEXT UNIQUE,
        title TEXT,
        company TEXT,
        raw_description TEXT,
        llm_score INTEGER,
        is_agency BOOLEAN,
        summary TEXT,
        processed_date TEXT
    )
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()

def job_exists(job_url: str) -> bool:
    """Checks if a job has already been processed."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM jobs WHERE job_url = ?", (job_url,))
        return cursor.fetchone() is not None

def insert_job(job_url, title, company, raw_description, llm_score, is_agency, summary):
    """Inserts a successfully processed job into the database."""
    query = """
    INSERT INTO jobs (job_url, title, company, raw_description, llm_score, is_agency, summary, processed_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                job_url, title, company, raw_description, llm_score, 
                is_agency, summary, datetime.utcnow().isoformat()
            ))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        # Catches the error if we accidentally try to insert a duplicate URL
        return False

# --- Testing Block ---
if __name__ == "__main__":
    print("Testing db.py...")
    init_db()
    print(f"Database initialized. Check your project folder for '{DB_PATH}'.")
"""
Database patch script for UAT Engine v2.
Adds Document table and new columns to test_cases_history.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "firstfintech_qa.db")

PATCHES = [
    # Document table
    """CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name VARCHAR(500) NOT NULL,
        file_type VARCHAR(20),
        domain VARCHAR(50),
        word_count INTEGER DEFAULT 0,
        page_count INTEGER DEFAULT 0,
        requirement_count INTEGER DEFAULT 0,
        role_count INTEGER DEFAULT 0,
        module_count INTEGER DEFAULT 0,
        parsed_structure TEXT,
        processing_status VARCHAR(50) DEFAULT 'uploaded',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )""",
    # New columns on test_cases_history
    "ALTER TABLE test_cases_history ADD COLUMN document_id INTEGER",
    "ALTER TABLE test_cases_history ADD COLUMN domain_detected VARCHAR(50)",
    "ALTER TABLE test_cases_history ADD COLUMN total_requirements INTEGER DEFAULT 0",
    "ALTER TABLE test_cases_history ADD COLUMN coverage_percentage FLOAT DEFAULT 0.0",
]


def run_patches():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for sql in PATCHES:
        try:
            cursor.execute(sql)
            print(f"OK:   {sql[:70]}...")
        except Exception as e:
            if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                print(f"SKIP: {sql[:70]}... (already exists)")
            else:
                print(f"ERR:  {sql[:70]}... => {e}")
    conn.commit()
    conn.close()
    print("\nDatabase patch complete.")


if __name__ == "__main__":
    run_patches()

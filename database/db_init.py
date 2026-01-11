import sqlite3
import os
from config import DB_PATH

def init_db():
    # Ensure directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    with open('database/schema.sql', 'r') as f:
        schema = f.read()
    
    conn.executescript(schema)
    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()

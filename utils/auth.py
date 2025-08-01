import sqlite3
import os
print("📂 Current Working Directory:", os.getcwd())
# Dynamically get the path to the database no matter where the script is run
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up from utils/
DB_PATH = os.path.join(BASE_DIR, "database", "user.db")

def validate_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def register_user(username, password):
    import os
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'user.db')
    conn = sqlite3.connect(os.path.abspath(db_path))

    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        print("✅ Registered:", username)
        return True
    except sqlite3.IntegrityError:
        print("⚠️ User already exists:", username)
        return False
    finally:
        conn.close()

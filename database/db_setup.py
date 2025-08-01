import sqlite3
import pandas as pd
import os

# Load CSVs correctly using ';' as separator
general_df = pd.read_csv("archive/clean_general_aptitude_dataset1.csv", sep=';', on_bad_lines='skip')
cse_df = pd.read_csv("archive/cse_dataset1.csv", sep=';', on_bad_lines='skip')
logical_df = pd.read_csv("archive/logical_reasoning_questions1.csv", sep=';', on_bad_lines='skip')

# Print to confirm correct headers
print("General Aptitude Columns:", general_df.columns)
print("CSE Columns:", cse_df.columns)
print("Logical Reasoning Columns:", logical_df.columns)

# ✅ Create and insert into quiz DB
def create_and_insert(table_name, df):
    conn = sqlite3.connect("database/quiz.db")
    cursor = conn.cursor()
    
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            option1 TEXT,
            option2 TEXT,
            option3 TEXT,
            option4 TEXT,
            answer TEXT
        )
    """)
    
    for _, row in df.iterrows():
        try:
            cursor.execute(f"""
                INSERT INTO {table_name} (question, option1, option2, option3, option4, answer)
                VALUES (?, ?, ?, ?, ?, ?)
            """, tuple(row[col] for col in ['question', 'option1', 'option2', 'option3', 'option4', 'answer']))
        except Exception as e:
            print(f"Skipping row due to error: {e}")
            continue

    conn.commit()
    conn.close()

# Load into tables
create_and_insert("general_quiz", general_df)
create_and_insert("cse_quiz", cse_df)
create_and_insert("logical_quiz", logical_df)

print("✅ All quiz tables created and data inserted.")



# Create user table (if not exists)
import os
db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'user.db')
conn = sqlite3.connect(os.path.abspath(db_path))
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
""")
# Example dummy user
try:
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("admin", "admin123"))
except:
    pass  # Ignore duplicate

conn.commit()
conn.close()
print("✅ User table ready.")

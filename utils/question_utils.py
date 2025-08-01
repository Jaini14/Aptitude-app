# utils/question_utils.py
import sqlite3

def get_questions_by_category(category):
    conn = sqlite3.connect("database/quiz.db")
    conn.row_factory = sqlite3.Row  # This allows access to columns by name like a dictionary
    cursor = conn.cursor()

    table_name = f"{category}_quiz"
    cursor.execute(f"SELECT * FROM {table_name} ORDER BY RANDOM() LIMIT 20")
    rows = cursor.fetchall()

    questions = [dict(row) for row in rows]  # Each row becomes a dictionary
    conn.close()
    return questions

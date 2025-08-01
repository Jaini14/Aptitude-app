import streamlit as st
import random
import sqlite3
import os
from chatbot import get_bot_response

# ------------- PATH CONFIG -------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DB_PATH = os.path.join(BASE_DIR, "database", "user.db")
QUIZ_DB_PATH = os.path.join(BASE_DIR, "database", "quiz.db")

# ------------- SESSION INIT -------------
for key, value in {
    'logged_in': False,
    'username': "",
    'questions': [],
    'current_q': 0,
    'score': 0,
    'quiz_active': False,
    'submitted_answers': {},
    'answer_feedback': {}
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ------------- AUTH FUNCTIONS -------------
def validate_user(username, password):
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def register_user(username, password):
    conn = sqlite3.connect(USER_DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# ------------- QUIZ FUNCTION -------------
def get_questions_by_category(category):
    conn = sqlite3.connect(QUIZ_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    table_name = f"{category}_quiz"
    cursor.execute(f"SELECT * FROM {table_name} ORDER BY RANDOM() LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ------------- LOGIN PAGE -------------
def login_page():
    st.title("🔐 Login / Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if validate_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("✅ Login successful!")
        else:
            st.error("❌ Invalid username or password.")

    if st.button("Register"):
        if register_user(username, password):
            st.success("✅ Registered. Now login.")
        else:
            st.warning("⚠️ Username already taken.")

# ------------- QUIZ PAGE -------------
def quiz_page():
    st.title("📝 Take a Quiz")

    def load_questions(category):
        questions = get_questions_by_category(category)
        random.shuffle(questions)
        st.session_state.questions = questions[:20]
        st.session_state.quiz_active = True
        st.session_state.current_q = 0
        st.session_state.submitted_answers = {}
        st.session_state.answer_feedback = {}
        st.session_state.score = 0

    if not st.session_state.quiz_active:
        category = st.selectbox("Choose a category", ["general", "cse", "logical"])
        if st.button("Start Quiz"):
            load_questions(category)
    else:
        questions = st.session_state.questions
        q_index = st.session_state.current_q
        q = questions[q_index]
        options = [q['option1'], q['option2'], q['option3'], q['option4']]
        submitted = q_index in st.session_state.submitted_answers

        st.write(f"**Q{q_index + 1} of {len(questions)}**")
        st.write(q['question'])

        radio_key = f"question_{q_index}_option"
        if submitted:
            selected_option = st.radio(
                "Options", options,
                index=options.index(st.session_state.submitted_answers[q_index]) if st.session_state.submitted_answers[q_index] in options else 0,
                key=radio_key, disabled=True
            )
        else:
            selected_option = st.radio("Options", options, index=None, key=radio_key)

        if not submitted and st.button("Submit Answer"):
            if selected_option:
                user_ans = selected_option.strip().lower()
                st.session_state.submitted_answers[q_index] = selected_option
                correct_label = q['answer'].strip().upper()
                correct_index = ord(correct_label) - ord('A')
                correct_option = options[correct_index].strip().lower()

                if user_ans == correct_option:
                    st.session_state.answer_feedback[q_index] = "✅ Correct!"
                else:
                    st.session_state.answer_feedback[q_index] = f"❌ Incorrect. Correct answer: {correct_label}"
            else:
                st.warning("Please select an option before submitting.")

        if q_index in st.session_state.answer_feedback:
            st.info(st.session_state.answer_feedback[q_index])

        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            if st.button("⬅️ Previous") and q_index > 0:
                st.session_state.current_q -= 1
        with col2:
            if st.button("➡️ Next"):
                if q_index < len(questions) - 1:
                    st.session_state.current_q += 1
        with col3:
            if q_index == len(questions) - 1 and st.button("✅ Finish Quiz"):
                total_correct = 0
                for i, q in enumerate(questions):
                    selected = st.session_state.submitted_answers.get(i, "").strip().lower()
                    correct_label = q['answer'].strip().upper()
                    correct_index = ord(correct_label) - ord('A')
                    correct_option = [q['option1'], q['option2'], q['option3'], q['option4']][correct_index].strip().lower()
                    if selected == correct_option:
                        total_correct += 1
                st.session_state.score = total_correct
                st.session_state.quiz_active = False

    if not st.session_state.quiz_active and st.session_state.questions:
        st.success(f"🎉 Quiz Finished! Your Score: {st.session_state.score}/{len(st.session_state.questions)}")
        if st.button("Restart"):
            for key in ['quiz_active', 'questions', 'current_q', 'submitted_answers', 'answer_feedback', 'score']:
                st.session_state[key] = 0 if isinstance(st.session_state[key], int) else []

# ------------- CHATBOT -------------
def chatbot_page():
    st.title("💬 Chatbot Assistant")
    user_query = st.text_input("Ask something...")
    if st.button("Ask"):
        response = get_bot_response(user_query)
        st.write(f"🤖 {response}")

# ------------- APP ROUTER -------------
if not st.session_state.logged_in:
    login_page()
else:
    page = st.sidebar.radio("📁 Navigation", ["Dashboard", "Quiz", "Chatbot"])
    st.sidebar.write(f"👤 Logged in as: `{st.session_state.username}`")

    if page == "Dashboard":
        st.title("📊 Welcome to the Aptitude App!")
        st.write("Use the sidebar to navigate to quiz or chatbot.")
    elif page == "Quiz":
        quiz_page()
    elif page == "Chatbot":
        chatbot_page()

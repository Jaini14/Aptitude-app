import streamlit as st
import requests
import random
from chatbot import get_bot_response
from utils.auth import register_user

BACKEND_URL = "http://127.0.0.1:5000"
st.set_page_config(page_title="Aptitude App", layout="centered")

# ------------------- Session State Init -------------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'current_q' not in st.session_state:
    st.session_state.current_q = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'quiz_active' not in st.session_state:
    st.session_state.quiz_active = False
if 'submitted_answers' not in st.session_state:
    st.session_state.submitted_answers = {}
if 'answer_feedback' not in st.session_state:
    st.session_state.answer_feedback = {}

# ------------------- Login/Register Page -------------------
def login_page():
    st.title("🔐 Login / Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        res = requests.post(f"{BACKEND_URL}/login", json={"username": username, "password": password})
        if res.ok and res.json().get("success"):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("✅ Login successful!")
        else:
            st.error("❌ Invalid username or password.")

    if st.button("Register"):
        if register_user(username, password):
            st.success("✅ User registered. Now you can login.")
        else:
            st.warning("⚠️ Username already taken.")

# ------------------- Load Questions -------------------
def load_questions(category):
    res = requests.post(f"{BACKEND_URL}/questions", json={"category": category})
    if res.ok:
        questions = res.json().get('questions', [])
        random.shuffle(questions)
        st.session_state.questions = questions[:20]
        st.session_state.current_q = 0
        st.session_state.score = 0
        st.session_state.quiz_active = True
        st.session_state.submitted_answers = {}
        st.session_state.answer_feedback = {}
    else:
        st.error("Failed to load questions.")

# ------------------- Quiz Page -------------------
def quiz_page():
    st.title("📝 Take a Quiz")

    if 'quiz_active' not in st.session_state:
        st.session_state.quiz_active = False
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'current_q' not in st.session_state:
        st.session_state.current_q = 0
    if 'submitted_answers' not in st.session_state:
        st.session_state.submitted_answers = {}
    if 'answer_feedback' not in st.session_state:
        st.session_state.answer_feedback = {}
    if 'score' not in st.session_state:
        st.session_state.score = 0

    def load_questions(category):
        from utils.question_utils import get_questions_by_category
        questions = get_questions_by_category(category)
        random.shuffle(questions)
        st.session_state.questions = questions[:20]  # Limit to 20 questions
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
                "Options",
                options,
                index=options.index(st.session_state.submitted_answers[q_index]) if st.session_state.submitted_answers[q_index] in options else 0,
                key=radio_key,
                disabled=True
            )
        else:
            selected_option = st.radio("Options", options, index=None, key=radio_key)

        if not submitted and st.button("Submit Answer"):
            if selected_option:
                user_ans = selected_option.strip().lower()
                st.session_state.submitted_answers[q_index] = selected_option

                correct_label = q['answer'].strip().upper()  # "A", "B", etc.
                correct_index = ord(correct_label) - ord('A')  # 0, 1, 2, 3
                correct_option = options[correct_index].strip().lower()

                if user_ans == correct_option:
                    st.session_state.answer_feedback[q_index] = "✅ Correct!"
                else:
                    st.session_state.answer_feedback[q_index] = f"❌ Incorrect. Correct answer: {correct_label}"
            else:
                st.warning("Please select an option before submitting.")

        if q_index in st.session_state.answer_feedback:
            st.info(st.session_state.answer_feedback[q_index])

        # ----------- NAVIGATION BUTTONS -----------
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

    # -------- SHOW SCORE --------
    if not st.session_state.quiz_active and st.session_state.questions:
        st.success(f"🎉 Quiz Finished! Your Score: {st.session_state.score}/{len(st.session_state.questions)}")
        if st.button("Restart"):
            st.session_state.quiz_active = False
            st.session_state.questions = []
            st.session_state.current_q = 0
            st.session_state.submitted_answers = {}
            st.session_state.answer_feedback = {}
            st.session_state.score = 0


# ------------------- Chatbot Page -------------------
def chatbot_page():
    st.title("💬 Chatbot Assistant")
    user_query = st.text_input("Ask something...")
    if st.button("Ask"):
        response = get_bot_response(user_query)
        st.write(f"🤖 {response}")

# ------------------- App Navigation -------------------
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

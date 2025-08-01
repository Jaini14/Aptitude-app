# chatbot.py
def get_bot_response(user_input):
    if "exam" in user_input.lower():
        return "Focus on practicing regularly and revise formulas!"
    elif "login" in user_input.lower():
        return "Use your registered username and password to login."
    else:
        return "I'm here to help you with your quiz and queries!"

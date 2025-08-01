# backend/flask_api.py
import sys
import os
from flask import Flask, request, jsonify

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from utils.auth import validate_user
from utils.question_utils import get_questions_by_category

app = Flask(__name__)

@app.route('/')
def home():
    return "Flask API is running."

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if validate_user(data['username'], data['password']):
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Invalid credentials"})

@app.route("/questions", methods=["POST"])
def get_questions():
    data = request.get_json()
    category = data.get("category")
    questions = get_questions_by_category(category)
    return jsonify({"questions": questions})

if __name__ == "__main__":
    
    app.run(host='0.0.0.0', port=5000)

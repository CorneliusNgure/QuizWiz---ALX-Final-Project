from app import app, db
import requests
from .models import User, QuizSession, QuestionAttempt
from flask import render_template, jsonify, request

@app.route("/home")
def home():   
    return render_template("home.html")


@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/sign_in")
def sign_in():
    return render_template("sign_in.html")

@app.route("/play")
def trivia_arena():
    return render_template("trivia_arena.html")

@app.route("/fetch_questions", methods=["GET"])
def fetch_questions():
    category = request.args.get("category")
    difficulty = request.args.get("difficulty")
    question_type = request.args.get("type")

    base_url = "https://opentdb.com/api.php"
    params = {
        "amount": 5, 
        "category": category,
        "difficulty": difficulty,
        "type": question_type
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to fetch questions"}), 500
    
@app.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    data = request.json
    user_id = data.get('user_id')
    answers = data.get('answers')  # List of answers with question text, user's answer, and correct answer

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    quiz_session = QuizSession(user_id=user_id)
    db.session.add(quiz_session)
    db.session.commit()

    score = 0
    for answer in answers:
        is_correct = answer['user_answer'] == answer['correct_answer']
        if is_correct:
            score += 1

        attempt = QuestionAttempt(
            quiz_session_id=quiz_session.id,
            question_text=answer['question_text'],
            user_answer=answer['user_answer'],
            correct_answer=answer['correct_answer'],
            is_correct=is_correct
        )
        db.session.add(attempt)

    quiz_session.score = score
    db.session.commit()

    return jsonify({"message": "Quiz results saved successfully", "score": score})
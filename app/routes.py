from flask import Blueprint, render_template, jsonify, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from .models import User, QuizSession, QuestionAttempt
import requests

# Define a blueprint
main_bp = Blueprint("main", __name__)

@main_bp.route("/home")
def home():
    return render_template("home.html")

@main_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        if User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first():
            flash("Username or Email already exists", "danger")
            return redirect(url_for("main.register"))

        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("main.sign_in"))
    
    return render_template("register.html")

@main_bp.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Login successful!", "success")
            return redirect(url_for("main.trivia_arena"))
        else:
            flash("Invalid email or password", "danger")
            return redirect(url_for("main.sign_in"))
    
    return render_template("sign_in.html")

@main_bp.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))

@main_bp.route("/play")
def trivia_arena():
    if "user_id" not in session:
        flash("Please log in to play.", "warning")
        return redirect(url_for("main.sign_in"))
    return render_template("trivia_arena.html")

@main_bp.route("/fetch_questions", methods=["GET"])
def fetch_questions():
    category = request.args.get("category")
    difficulty = request.args.get("difficulty")
    question_type = request.args.get("type")

    base_url = "https://opentdb.com/api.php"
    params = {
        "amount": 10, 
        "category": category,
        "difficulty": difficulty,
        "type": question_type
    }

    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to fetch questions"}), 500

@main_bp.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized access"}), 401

    data = request.json
    user_id = session["user_id"]
    answers = data.get('answers')  # List of answers with question text, user's answer, and correct answer

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # a new quiz session to store quiz data
    quiz_session = QuizSession(user_id=user_id)
    db.session.add(quiz_session)
    db.session.commit()

    score = 0
    for answer in answers:
        is_correct = answer['user_answer'] == answer['correct_answer']
        if is_correct:
            score += 1

        # Store each question attempt
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
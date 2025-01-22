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

        if User.query.filter((User.email == email) | (User.username == username)).first():
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

    if not category or not difficulty or not question_type:
        return jsonify({"message": "Missing query parameters"}), 400

    base_url = "https://opentdb.com/api.php"
    params = {
        "amount": 10,
        "category": category,
        "difficulty": difficulty,
        "type": question_type
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        if not data.get("results"):
            return jsonify({"message": "No questions found"}), 404

        # Ensure the response matches client expectations
        return jsonify({"results": data["results"]})
    except requests.RequestException as e:
        return jsonify({"message": f"Failed to fetch questions: {str(e)}"}), 500


@main_bp.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized access"}), 401

    data = request.get_json()
    print("Received data:", data)  # Debug incoming payload

    if not data or "answers" not in data:
        print("Invalid input received.")
        return jsonify({"error": "Invalid input"}), 400

    user_id = session["user_id"]
    answers = data["answers"]
    print("Answers received:", answers)  # Debug answers array

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    quiz_session = QuizSession(user_id=user_id)
    db.session.add(quiz_session)
    db.session.commit()

    score = 0
    for answer in answers:
        print("Processing answer:", answer)  # Debug each answer

        # Normalize and strip user_answer
        user_answer = answer.get('user_answer', 'N/A').split(". ", 1)[-1].strip().lower()
        correct_answer = answer.get('correct_answer', 'N/A').strip().lower()

        print(f"Comparing: user_answer='{user_answer}' vs correct_answer='{correct_answer}'")

        is_correct = user_answer == correct_answer
        if is_correct:
            score += 1

        attempt = QuestionAttempt(
            quiz_session_id=quiz_session.id,
            question_text=answer.get('question_text', 'N/A'),
            user_answer=answer.get('user_answer', 'N/A'),
            correct_answer=answer.get('correct_answer', 'N/A'),
            is_correct=is_correct
        )
        db.session.add(attempt)

    quiz_session.score = score
    db.session.commit()
    print("Final score:", score)  # Debug final score

    return jsonify({"message": "Quiz results saved successfully", "score": score})
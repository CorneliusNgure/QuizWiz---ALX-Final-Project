from flask import Blueprint, render_template, jsonify, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from .models import User, QuizSession, QuestionAttempt, Question, Scoring, QuestionCategory, QuestionDifficulty, QuestionType
import requests
import json

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


import logging

@main_bp.route("/fetch_questions", methods=["GET"])
def fetch_questions():
    category = request.args.get("category")
    difficulty = request.args.get("difficulty")
    question_type = request.args.get("type")

    if not category or not difficulty or not question_type:
        return jsonify({"message": "Missing query parameters"}), 400

    # Map category, difficulty, and type names to their IDs
    category_obj = QuestionCategory.query.filter_by(name=category).first()
    difficulty_obj = QuestionDifficulty.query.filter_by(level=difficulty).first()
    type_obj = QuestionType.query.filter_by(type=question_type).first()

    # Validate that all mappings exist
    if not category_obj:
        return jsonify({"message": f"Category '{category}' not found"}), 404
    if not difficulty_obj:
        return jsonify({"message": f"Difficulty '{difficulty}' not found"}), 404
    if not type_obj:
        return jsonify({"message": f"Type '{question_type}' not found"}), 404

    category_id = category_obj.id
    difficulty_id = difficulty_obj.id
    type_id = type_obj.id

    # Fetch questions from the API
    base_url = "https://opentdb.com/api.php"
    params = {
        "amount": 3,
        "category": category_id,
        "difficulty": difficulty,
        "type": question_type
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

        # Debug: Log the response data from the API
        logging.info("Fetched data from OpenTDB API: %s", data)

        if not data.get("results"):
            return jsonify({"message": "No questions found"}), 404

        saved_questions = []

        for item in data["results"]:
            # Check if the question already exists in the database
            question = Question.query.filter_by(question_text=item["question"]).first()

            if not question:
                question = Question(
                    question_text=item["question"],
                    correct_answer=item["correct_answer"],
                    category_id=category_id,
                    difficulty_id=difficulty_id,
                    type_id=type_id,
                )
                db.session.add(question)
                db.session.commit()
            
            saved_questions.append({
                "id": question.id,
                "question": question.question_text,
                "correct_answer": question.correct_answer,
            })

        # Debug: Log the saved questions
        logging.info("Saved questions: %s", saved_questions)

        return jsonify({"results": saved_questions})

    except requests.RequestException as e:
        logging.error("Failed to fetch questions from API: %s", str(e))
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
    print("Answers received:", answers)

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Create a new quiz session
    quiz_session = QuizSession(user_id=user_id)
    db.session.add(quiz_session)
    db.session.commit()

    total_score = 0

    for answer in answers:
        question_id = answer.get("question_id")
        if not question_id:
            print("Missing question_id in answer:", answer)
            continue  # Skip or handle this as needed

        user_answer = answer.get("user_answer")

        question = Question.query.get(question_id)
        if not question:
            print(f"Question with ID {question_id} not found in the database.")
            continue

        # Check if the answer is correct
        is_correct = (user_answer.strip().lower() == question.correct_answer.strip().lower())

        # Fetch points for this question
        scoring_rule = Scoring.query.filter_by(
            category_id=question.category_id,
            difficulty_id=question.difficulty_id,
            type_id=question.type_id
        ).first()

        points_awarded = scoring_rule.points if scoring_rule and is_correct else 0
        total_score += points_awarded

        # Save the question attempt
        question_attempt = QuestionAttempt(
            quiz_session_id=quiz_session.id,
            question_id=question.id,
            user_answer=user_answer,
            is_correct=is_correct,
            points_awarded=points_awarded
        )
        db.session.add(question_attempt)

    # Update the quiz session's score
    quiz_session.score = total_score
    db.session.commit()

    return jsonify({
        "message": "Quiz submitted successfully!",
        "total_score": total_score
    })
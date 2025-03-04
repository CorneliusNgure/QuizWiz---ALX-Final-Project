from flask import Blueprint, render_template, jsonify, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, mail
from .models import User, QuizSession, QuestionAttempt, Question, Scoring, QuestionCategory, QuestionDifficulty, QuestionType
import requests
import html
from decimal import Decimal
from datetime import datetime
import json
from sqlalchemy import desc, func
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

# Define the serializer using the secret key
s = URLSafeTimedSerializer(SECRET_KEY)

# Blueprint definition
main_bp = Blueprint("main", __name__)

@main_bp.route("/")
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
    session.pop("email", None)
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
    # Fetch query parameters from the request
    category = request.args.get("category")
    difficulty = request.args.get("difficulty")
    question_type = request.args.get("type")

    # Validate the inputs
    if not category or not difficulty or not question_type:
        return jsonify({"message": "Missing query parameters"}), 400

    try:
        # Prepare parameters for the API request
        base_url = "https://opentdb.com/api.php"
        params = {
            "amount": 3,
            "category": category,  # Directly use the category ID from the frontend
            "difficulty": difficulty, 
            "type": question_type, 
        }

        # print(f"Fetching questions with params: {params}")

        # Fetch questions from Open Trivia API
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        print(f"Data from API: {data}")

        if not data.get("results"):
            return jsonify({"message": "No questions found"}), 404

        # Initialize a list for questions to be committed to the database
        new_questions = []

        for item in data["results"]:
            # Decode HTML entities in the question text and incorrect answers
            question_text = html.unescape(item["question"])
            incorrect_answers = [html.unescape(answer) for answer in item["incorrect_answers"]]
            
            # Check if the question already exists in the database
            existing_question = Question.query.filter_by(question_text=item["question"]).first()

            if not existing_question:
                # Mapping difficulty and type to their respective IDs
                difficulty_id = 1 if difficulty == "easy" else 2 if difficulty == "medium" else 3
                type_id = 1 if question_type == "multiple" else 2

                # new Question object
                new_question = Question(
                    question_text=question_text,
                    correct_answer=item["correct_answer"],
                    incorrect_answers=incorrect_answers,
                    category_id=int(category),  
                    difficulty_id=difficulty_id,  
                    type_id=type_id,  
                )
                new_questions.append(new_question)

        # Bulk insert new questions if any
        if new_questions:
            db.session.bulk_save_objects(new_questions)
            db.session.commit()

        # Fetch all matching questions from the database, including new and existing
        saved_questions = Question.query.filter(
            Question.category_id == int(category),
            Question.difficulty_id == difficulty_id,
            Question.type_id == type_id
        ).limit(5).all()

        response_questions = [
            {
                "id": question.id,
                "question": question.question_text,
                "correct_answer": question.correct_answer,
                "incorrect_answers": question.incorrect_answers,
            }
            for question in saved_questions
        ]

        return jsonify({"results": response_questions}), 200
    
    except ValueError as e:
        print(f"ValueError: {str(e)}")
        return jsonify({"message": "Invalid input parameters"}), 400
    except requests.RequestException as e:
        print(f"Failed to fetch questions from API: {str(e)}")
        return jsonify({"message": f"Failed to fetch questions: {str(e)}"}), 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return jsonify({"message": "Failed to fetch questions"}), 500


@main_bp.route("/submit_quiz", methods=["POST"])
def submit_quiz():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized access"}), 401

    data = request.get_json()
    # print("Received data:", data) 
    
    if not data or "answers" not in data:
        # print("Invalid input received.")
        return jsonify({"error": "Invalid input"}), 400

    user_id = session["user_id"]
    answers = data["answers"]
    # print("Answers received:", answers)

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if not answers:
        return jsonify({"error": "No answers provided"}), 400

    first_question_id = answers[0].get("question_id")
    first_question = Question.query.filter(Question.id == first_question_id).first()
    if not first_question:
        return jsonify({"error": "Invalid quiz data"}), 400

    category_id = first_question.category_id
    difficulty_id = first_question.difficulty_id
    type_id = first_question.type_id

    # Creating a new quiz session
    quiz_session = QuizSession(
        user_id=user_id,
        category_id=category_id,
        difficulty_id=difficulty_id,
        type_id=type_id
    )
    db.session.add(quiz_session)
    db.session.commit()

    total_score = 0

    for answer in answers:
        question_id = answer.get("question_id")
        if not question_id:
            print("Missing question_id in answer:", answer)
            continue  # Skip invalid answer

        user_answer = answer.get("selected_answer")
        question = Question.query.filter(Question.id == question_id).first()
        if not question:
            print(f"Question with ID {question_id} not found in the database.")
            continue
        else:
            print(user_answer)


        correct_answer = question.correct_answer if question.correct_answer else ""
        is_correct = (user_answer.strip().lower() == correct_answer.strip().lower())

        # fetching questions from scoring table
        scoring_rule = Scoring.query.filter_by(
            # category_id=question.category_id,
            difficulty_id=question.difficulty_id,
            type_id=question.type_id
        ).first()

        points_awarded = scoring_rule.points if scoring_rule and is_correct else 0
        total_score += points_awarded

        # Saving the question attempt
        question_attempt = QuestionAttempt(
            quiz_session_id=quiz_session.id,
            question_id=question.id,
            user_answer=user_answer,
            is_correct=is_correct,
            points_awarded=points_awarded
        )
        db.session.add(question_attempt)

    # Updating the quiz session's score
    quiz_session.score = total_score
    db.session.commit()

    return jsonify({
        "message": "Quiz submitted successfully!",
        "total_score": total_score
    })


@main_bp.route("/analytics", methods=["GET"])
def analytics():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    # print(f"Fetching analytics for user_id: {user_id}")

    # Converting Decimal to int or float.
    def serialize_decimal(value):
        if isinstance(value, Decimal):
            return int(value) if value % 1 == 0 else float(value)
        return value

    # Converting datetime to string (ISO format)
    def serialize_datetime(value):
        return value.isoformat() if isinstance(value, datetime) else value

    try:
        # Fetching user rankings
        rankings = db.session.query(
            User.username, func.sum(QuizSession.score).label("total_score")
        ).join(QuizSession).group_by(User.id).order_by(desc("total_score")).all()

        rankings = [{"username": r.username, "total_score": serialize_decimal(r.total_score)} for r in rankings]
    except Exception as e:
        print(f"Error fetching rankings: {e}")
        rankings = []

    try:
        # Fetching category, difficulty, and type mappings
        category_map = {c.id: c.name for c in db.session.query(QuestionCategory.id, QuestionCategory.name).all()}
        difficulty_map = {d.id: d.level for d in db.session.query(QuestionDifficulty.id, QuestionDifficulty.level).all()}
        type_map = {t.id: t.type for t in db.session.query(QuestionType.id, QuestionType.type).all()}

        # Fetching user quiz results (join to get category, difficulty, type)
        user_results = (
            db.session.query(
                QuizSession.id,
                QuizSession.score,
                QuizSession.created_at,
                func.min(Question.category_id).label("category_id"),  # Pick one category
                func.min(Question.difficulty_id).label("difficulty_id"),  # Pick one difficulty
                func.min(Question.type_id).label("type_id")  # Pick one type
                )
                .join(QuestionAttempt, QuizSession.id == QuestionAttempt.quiz_session_id)
                .join(Question, Question.id == QuestionAttempt.question_id)
                .filter(QuizSession.user_id == user_id)
                .group_by(QuizSession.id, QuizSession.score, QuizSession.created_at)  # Group by quiz session
                .order_by(desc(QuizSession.created_at))
                .all()
                )

        # Converting to readable format instead of IDs
        user_results = [
            {
                "quiz_id": r.id,
                "category": category_map.get(r.category_id, "Unknown"),
                "difficulty": difficulty_map.get(r.difficulty_id, "Unknown"),
                "type": type_map.get(r.type_id, "Unknown"),
                "score": serialize_decimal(r.score),
                "timestamp": serialize_datetime(r.created_at)
            }
            for r in user_results
        ]
    except Exception as e:
        # print(f"Error fetching user results: {e}")
        user_results = []

    try:
        # Fetching performance breakdown by difficulty
        difficulty_performance = (
            db.session.query(
                Question.difficulty_id,
                func.count(QuestionAttempt.id).label("total_attempts"),
                func.sum(QuestionAttempt.is_correct).label("correct_answers")
            )
            .join(QuestionAttempt, Question.id == QuestionAttempt.question_id)
            .join(QuizSession, QuizSession.id == QuestionAttempt.quiz_session_id)
            .filter(QuizSession.user_id == user_id)
            .group_by(Question.difficulty_id).all()
        )

        difficulty_performance = [
            {
                "difficulty": difficulty_map.get(d.difficulty_id, "Unknown"),
                "total_attempts": d.total_attempts,
                "correct_answers": d.correct_answers
            }
            for d in difficulty_performance
        ]
    except Exception as e:
        print(f"Error fetching difficulty performance: {e}")
        difficulty_performance = []

    try:
        # Fetching category performance
        category_performance = (
            db.session.query(
                Question.category_id,
                func.count(QuestionAttempt.id).label("total_attempts"),
                func.sum(QuestionAttempt.is_correct).label("correct_answers")
            )
            .join(QuestionAttempt, Question.id == QuestionAttempt.question_id)
            .join(QuizSession, QuizSession.id == QuestionAttempt.quiz_session_id)
            .filter(QuizSession.user_id == user_id)
            .group_by(Question.category_id).all()
        )

        category_performance = [
            {
                "category": category_map.get(c.category_id, "Unknown"),
                "total_attempts": c.total_attempts,
                "correct_answers": c.correct_answers
            }
            for c in category_performance
        ]
    except Exception as e:
        print(f"Error fetching category performance: {e}")
        category_performance = []

    # Calculating the quiz summary
    total_quizzes = len(user_results)
    average_score = (
        sum([r["score"] if r["score"] is not None else 0 for r in user_results]) / total_quizzes
        if total_quizzes > 0 else 0
    )

    quiz_summary = {
        "total_quizzes": total_quizzes,
        "average_score": round(average_score, 2)
    }

    # Calculating the score trend
    if total_quizzes > 1:
        first_half = user_results[:total_quizzes // 2]
        second_half = user_results[total_quizzes // 2:]

        first_half_avg = sum([q["score"] for q in first_half]) / len(first_half) if first_half else 0
        second_half_avg = sum([q["score"] for q in second_half]) / len(second_half) if second_half else 0

        score_trend = "improving" if second_half_avg > first_half_avg else "declining"
    else:
        score_trend = "insufficient data"

    # Converting analytics data to JSON and pass it to the template
    analytics_data = json.dumps({
        "rankings": rankings,
        "user_results": user_results,
        "difficulty_performance": difficulty_performance,
        "category_performance": category_performance,
        "quiz_summary": quiz_summary,
        "score_trend": score_trend
    })

    # print("Analytics Data:", analytics_data)

    return render_template("analytics.html", analytics_data=analytics_data)


@main_bp.route("/forgot_password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form["email"]
        user = User.query.filter_by(email=email).first()

        if user:
            token = s.dumps(email, salt="password-reset-salt")
            reset_url = url_for("main.reset_password", token=token, _external=True)

            # Send email with reset link
            msg = Message("Password Reset Request", recipients=[email])
            msg.body = f"Click the link to reset your password: {reset_url}"
            print("Attempting to send email...")
            mail.send(msg)
            print("Email sent successfully!")

            flash("A password reset link has been sent to your email.", "info")
        else:
            flash("Email not found. Please check again.", "danger")
        return redirect(url_for("main.forgot_password"))

    return render_template("forgot_password.html")


@main_bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = s.loads(token, salt="password-reset-salt", max_age=3600)  # Token expires in 1 hour
    except:
        flash("The password reset link is invalid or has expired.", "danger")
        return redirect(url_for("main.forgot_password"))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash("Invalid email address.", "danger")
        return redirect(url_for("main.forgot_password"))

    if request.method == "POST":
        new_password = request.form["password"]
        user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash("Your password has been reset. You can now sign in.", "success")
        return redirect(url_for("main.sign_in"))

    return render_template("reset_password.html")
from flask import Blueprint, render_template, jsonify, request, redirect, url_for, session, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from .models import User, QuizSession, QuestionAttempt, Question, Scoring, QuestionCategory, QuestionDifficulty, QuestionType
import requests
import json
import logging
import html

# Define a blueprint
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
            "difficulty": difficulty,  # Pass difficulty as-is
            "type": question_type,  # Pass type as-is
        }

        print(f"Fetching questions with params: {params}")

        # Fetch questions from Open Trivia API
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        print(f"API response: {data}")

        # Check if the API returned any questions
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
                # Map difficulty and type to their respective IDs
                difficulty_id = 1 if difficulty == "easy" else 2 if difficulty == "medium" else 3
                type_id = 1 if question_type == "multiple" else 2

                # Create a new Question object
                new_question = Question(
                    question_text=question_text,
                    correct_answer=item["correct_answer"],
                    incorrect_answers=incorrect_answers,
                    category_id=int(category),  # Store the category ID
                    difficulty_id=difficulty_id,  # Map difficulty levels
                    type_id=type_id,  # Map type IDs
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
        ).all()

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
        return jsonify({"message": "An unexpected error occurred"}), 500


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

    if not answers:
        return jsonify({"error": "No answers provided"}), 400

    first_question_id = answers[0].get("question_id")
    first_question = Question.query.filter(Question.id == first_question_id).first()
    if not first_question:
        return jsonify({"error": "Invalid quiz data"}), 400

    category_id = first_question.category_id
    difficulty_id = first_question.difficulty_id
    type_id = first_question.type_id

    # Create a new quiz session
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

        # fetch questions from scoring table
        scoring_rule = Scoring.query.filter_by(
            # category_id=question.category_id,
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


@main_bp.route("/data_analytics", methods=["GET"])
def data_analytics():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized access"}), 401

    user_id = session["user_id"]
    print(f"Fetching analytics for user_id: {user_id}")

    # Fetch user rankings
    try:
        rankings = db.session.query(
            User.id, User.username, db.func.sum(QuizSession.score).label("total_score")
        ).join(QuizSession).group_by(User.id).order_by(db.desc("total_score")).all()
        print("Rankings fetched successfully.")
    except Exception as e:
        print(f"Error fetching rankings: {e}")
        rankings = []

    # Fetch user quiz results
    try:
        user_results = db.session.query(
            QuizSession.id, QuizSession.score, QuizSession.created_at
        ).filter_by(user_id=user_id).order_by(db.desc(QuizSession.created_at)).all()
        print("User results fetched successfully.")
    except Exception as e:
        print(f"Error fetching user results: {e}")
        user_results = []

    # Fetch performance breakdown
    try:
        difficulty_performance = (
            db.session.query(
            Question.difficulty_id, db.func.count(QuestionAttempt.id).label("total_attempts"),
            db.func.sum(QuestionAttempt.is_correct).label("correct_answers")
        )
        .join(QuestionAttempt, Question.id == QuestionAttempt.question_id)
        .join(QuizSession, QuizSession.id == QuestionAttempt.quiz_session_id)
        .filter(QuizSession.user_id == user_id)
        .group_by(Question.difficulty_id).all()
        )

        print("Difficulty performance data fetched successfully.")
    except Exception as e:
        print(f"Error fetching difficulty performance: {e}")
        difficulty_performance = []

    # Fetch category performance
    try:
        category_performance = (
            db.session.query(
            Question.category_id, db.func.count(QuestionAttempt.id).label("total_attempts"),
            db.func.sum(QuestionAttempt.is_correct).label("correct_answers")
        )
        .join(QuestionAttempt, Question.id == QuestionAttempt.question_id) 
        .join(QuizSession, QuizSession.id == QuestionAttempt.quiz_session_id)
        .filter(QuizSession.user_id == user_id)
        .group_by(Question.category_id).all()
        )

        print("Category performance data fetched successfully.")
    except Exception as e:
        print(f"Error fetching category performance: {e}")
        category_performance = []

    # Prepare response
    response = {
        "rankings": [{
            "user_id": rank[0], "username": rank[1], "total_score": rank[2]
        } for rank in rankings],
        "user_results": [{
            "quiz_id": result[0], "score": result[1], "timestamp": result[2]
        } for result in user_results],
        "difficulty_performance": [{
            "difficulty_id": dp[0], "total_attempts": dp[1], "correct_answers": dp[2]
        } for dp in difficulty_performance],
        "category_performance": [{
            "category_id": cp[0], "total_attempts": cp[1], "correct_answers": cp[2]
        } for cp in category_performance]
    }
    print("Analytics response prepared successfully.")
    print(response)
    return render_template('analytics.html')


    
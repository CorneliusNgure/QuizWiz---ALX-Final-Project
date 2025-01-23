from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    quiz_sessions = db.relationship('QuizSession', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hashes and stores the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifies the user's password."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class QuizSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('question_category.id', ondelete='SET NULL'), nullable=True, index=True)
    difficulty_id = db.Column(db.Integer, db.ForeignKey('question_difficulty.id', ondelete='SET NULL'), nullable=True, index=True)
    type_id = db.Column(db.Integer, db.ForeignKey('question_type.id', ondelete='SET NULL'), nullable=True, index=True)
    score = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = db.relationship('QuestionCategory', backref='quiz_sessions', lazy=True)
    difficulty = db.relationship('QuestionDifficulty', backref='quiz_sessions', lazy=True)
    question_type = db.relationship('QuestionType', backref='quiz_sessions', lazy=True)
    attempts = db.relationship('QuestionAttempt', backref='quiz_session', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return (
            f"<QuizSession id={self.id}, user_id={self.user_id}, "
            f"category_id={self.category_id}, difficulty_id={self.difficulty_id}, "
            f"type_id={self.type_id}, score={self.score}>"
        )


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('question_category.id', ondelete='CASCADE'), nullable=False, index=True)
    difficulty_id = db.Column(db.Integer, db.ForeignKey('question_difficulty.id', ondelete='CASCADE'), nullable=False, index=True)
    type_id = db.Column(db.Integer, db.ForeignKey('question_type.id', ondelete='CASCADE'), nullable=False, index=True)
    correct_answer = db.Column(db.Text, nullable=False)
    attempts = db.relationship('QuestionAttempt', backref='question', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Question {self.id}: {self.question_text[:50]}...>"


class QuestionCategory(db.Model):
    """
    Represents categories of questions (e.g., "Science").
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)

    def __repr__(self):
        return f"<QuestionCategory {self.name}>"


class QuestionDifficulty(db.Model):
    """
    Represents difficulty levels for the questions.
    """
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(
        db.Enum('easy', 'medium', 'hard', name='question_difficulty_levels'),
        unique=True,
        nullable=False
    )

    def __repr__(self):
        return f"<QuestionDifficulty {self.level}>"


class QuestionType(db.Model):
    """
    Represents types of questions (e.g., "multiple choice", "true/false").
    """
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(
        db.Enum('multiple choice', 'true/false', name='question_types'),
        unique=True,
        nullable=False
    )

    def __repr__(self):
        return f"<QuestionType {self.type}>"


class QuestionAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_session_id = db.Column(db.Integer, db.ForeignKey('quiz_session.id', ondelete='CASCADE'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id', ondelete='CASCADE'), nullable=False, index=True)
    user_answer = db.Column(db.Text, nullable=True)
    is_correct = db.Column(db.Boolean, nullable=False)
    points_awarded = db.Column(db.Integer, default=0)
    date_attempted = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<QuestionAttempt {self.id}, Correct: {self.is_correct}>"


class Scoring(db.Model):
    """
    Represents the scoring system for questions based on difficulty, type, and category.
    """
    id = db.Column(db.Integer, primary_key=True)
    difficulty_id = db.Column(db.Integer, db.ForeignKey('question_difficulty.id', ondelete='CASCADE'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('question_type.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('question_category.id', ondelete='CASCADE'), nullable=True)  # Nullable in case scoring isn't category-specific
    points = db.Column(db.Integer, nullable=False)

    # Relationships
    difficulty = db.relationship('QuestionDifficulty', backref='scoring_rules', lazy=True)
    question_type = db.relationship('QuestionType', backref='scoring_rules', lazy=True)
    category = db.relationship('QuestionCategory', backref='scoring_rules', lazy=True)

    def __repr__(self):
        return (
            f"<Scoring Difficulty={self.difficulty.level}, "
            f"Type={self.question_type.type}, "
            f"Category={self.category.name if self.category else 'None'}, "
            f"Points={self.points}>"
        )
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    quiz_sessions = db.relationship('QuizSession', backref='user', lazy=True)

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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('quiz_category.id'), nullable=True)
    difficulty_id = db.Column(db.Integer, db.ForeignKey('quiz_difficulty.id'), nullable=True)
    type_id = db.Column(db.Integer, db.ForeignKey('quiz_type.id'), nullable=True)
    score = db.Column(db.Integer, nullable=True)

    # Relationships
    category = db.relationship('QuizCategory', backref='quiz_sessions', lazy=True)
    difficulty = db.relationship('QuizDifficulty', backref='quiz_sessions', lazy=True)
    type = db.relationship('QuizType', backref='quiz_sessions', lazy=True)

    def __repr__(self):
        return (
            f"<QuizSession id={self.id}, user_id={self.user_id}, "
            f"category_id={self.category_id}, difficulty_id={self.difficulty_id}, "
            f"type_id={self.type_id}, score={self.score}>"
        )



class QuestionAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_session_id = db.Column(db.Integer, db.ForeignKey('quiz_session.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)  # Keep as Text for flexibility
    is_correct = db.Column(db.Boolean, nullable=False)
    user_answer = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<QuestionAttempt {self.id} - Correct: {self.is_correct}>"
    

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
        db.Enum('easy', 'medium', 'hard', name='difficulty_levels'),
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


from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    quiz_sessions = db.relationship('QuizSession', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

class QuizSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_started = db.Column(db.DateTime, default=datetime.utcnow)
    score = db.Column(db.Integer, nullable=True)
    questions_attempted = db.relationship('QuestionAttempt', backref='quiz_session', lazy=True)

    def __repr__(self):
        return f"<QuizSession {self.id} for User {self.user_id}>"

class QuestionAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_session_id = db.Column(db.Integer, db.ForeignKey('quiz_session.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    user_answer = db.Column(db.String(255), nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<QuestionAttempt {self.id} - Correct: {self.is_correct}>"
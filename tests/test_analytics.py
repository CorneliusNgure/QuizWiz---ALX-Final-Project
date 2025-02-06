import pytest
from flask import session, url_for
from app import create_app, db
from app.models import User, QuizSession, Question, QuestionAttempt, QuestionCategory, QuestionDifficulty, QuestionType
from decimal import Decimal
from datetime import datetime

@pytest.fixture
def client():
    app = create_app('testing') 
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

@pytest.fixture
def setup_user():
    user = User(username='testuser', email='test@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()
    return user

def login(client, user):
    with client.session_transaction() as sess:
        sess['user_id'] = user.id

def test_analytics_authenticated(client, setup_user):
    user = setup_user
    login(client, user)

    # Setting up mock data
    category = QuestionCategory(name='Science')
    difficulty = QuestionDifficulty(level='Easy')
    qtype = QuestionType(type='Multiple Choice')
    db.session.add_all([category, difficulty, qtype])
    db.session.commit()

    question = Question(category_id=category.id, difficulty_id=difficulty.id, type_id=qtype.id)
    db.session.add(question)
    db.session.commit()

    quiz_session = QuizSession(user_id=user.id, score=Decimal('85.5'), created_at=datetime.utcnow())
    db.session.add(quiz_session)
    db.session.commit()

    attempt = QuestionAttempt(quiz_session_id=quiz_session.id, question_id=question.id, is_correct=True)
    db.session.add(attempt)
    db.session.commit()

    response = client.get('/analytics')
    assert response.status_code == 200
    assert b'analytics_data' in response.data

def test_analytics_unauthenticated(client):
    response = client.get('/analytics')
    assert response.status_code == 302 
    assert url_for('auth.login') in response.headers['Location']

def test_analytics_no_data(client, setup_user):
    user = setup_user
    login(client, user)

    response = client.get('/analytics')
    assert response.status_code == 200
    assert b'analytics_data' in response.data
    assert b'"rankings": []' in response.data
    assert b'"user_results": []' in response.data
    assert b'"difficulty_performance": []' in response.data
    assert b'"category_performance": []' in response.data
    assert b'"total_quizzes": 0' in response.data
    assert b'"average_score": 0' in response.data
    assert b'"score_trend": "insufficient data"' in response.data
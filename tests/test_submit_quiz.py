import pytest
from unittest.mock import patch
from app.models import User, Question, QuizSession, QuestionAttempt, Scoring
from flask import session

@pytest.fixture
def logged_in_client(client, db_session):
    """Fixture to log in a test user."""
    test_user = User(id=1, username='testuser', email='test@example.com')
    db_session.add(test_user)
    db_session.commit()

    with client.session_transaction() as sess:
        sess['user_id'] = test_user.id
    
    yield client


def test_submit_quiz_success(logged_in_client, db_session):
    """Test successful quiz submission."""
    # Setup mock data
    question = Question(id=1, correct_answer='Paris', category_id=1, difficulty_id=1, type_id=1)
    scoring_rule = Scoring(difficulty_id=1, type_id=1, points=10)
    db_session.add_all([question, scoring_rule])
    db_session.commit()

    answers = [{"question_id": 1, "selected_answer": "Paris"}]

    response = logged_in_client.post('/submit_quiz', json={"answers": answers})

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == "Quiz submitted successfully!"
    assert data['total_score'] == 10


def test_submit_quiz_unauthorized(client):
    """Test quiz submission without logging in."""
    response = client.post('/submit_quiz', json={"answers": []})

    assert response.status_code == 401
    data = response.get_json()
    assert data['error'] == "Unauthorized access"


def test_submit_quiz_invalid_input(logged_in_client):
    """Test quiz submission with invalid input."""
    response = logged_in_client.post('/submit_quiz', json={})

    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == "Invalid input"


def test_submit_quiz_user_not_found(client, db_session):
    """Test quiz submission when user is not found."""
    with client.session_transaction() as sess:
        sess['user_id'] = 999 

    response = client.post('/submit_quiz', json={"answers": []})

    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == "User not found"


def test_submit_quiz_no_answers(logged_in_client):
    """Test quiz submission with no answers provided."""
    response = logged_in_client.post('/submit_quiz', json={"answers": []})

    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == "No answers provided"


def test_submit_quiz_invalid_question(logged_in_client):
    """Test quiz submission with invalid question ID."""
    answers = [{"question_id": 999, "selected_answer": "Paris"}]  # Non-existent question ID

    response = logged_in_client.post('/submit_quiz', json={"answers": answers})

    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == "Invalid quiz data"
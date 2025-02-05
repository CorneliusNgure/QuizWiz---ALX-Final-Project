import pytest
from unittest.mock import patch
import json

def test_fetch_questions_success(client):
    """Test successful fetching of trivia questions"""
    mock_api_response = {
        "results": [
            {
                "question": "What is the capital of France?",
                "correct_answer": "Paris",
                "incorrect_answers": ["Lyon", "Marseille", "Toulouse"]
            },
            {
                "question": "Which planet is known as the Red Planet?",
                "correct_answer": "Mars",
                "incorrect_answers": ["Earth", "Jupiter", "Venus"]
            },
            {
                "question": "What is the largest ocean on Earth?",
                "correct_answer": "Pacific Ocean",
                "incorrect_answers": ["Atlantic Ocean", "Indian Ocean", "Arctic Ocean"]
            }
        ]
    }

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_api_response

        response = client.get('/fetch_questions?category=9&difficulty=easy&type=multiple')

        assert response.status_code == 500
        data = response.get_json()
        assert len(data['results']) == 5
        assert data['results'][0]['question'] == "What is the capital of France?"

def test_fetch_questions_missing_params(client):
    """Test fetching questions with missing query parameters"""
    response = client.get('/fetch_questions?category=9&difficulty=easy')

    assert response.status_code == 400
    assert b"Missing query parameters" in response.data

def test_fetch_questions_no_results(client):
    """Test fetching questions when API returns no results"""
    mock_api_response = {"results": []}

    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_api_response

        response = client.get('/fetch_questions?category=9&difficulty=easy&type=multiple')

        assert response.status_code == 404
        assert b"No questions found" in response.data

def test_fetch_questions_invalid_input(client):
    """Test fetching questions with invalid category parameter"""
    response = client.get('/fetch_questions?category=invalid&difficulty=easy&type=multiple')

    assert response.status_code == 400
    assert b"Invalid input parameters" in response.data

def test_fetch_questions_api_failure(client):
    """Test API failure during fetching questions"""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = Exception("API unreachable")

        response = client.get('/fetch_questions?category=9&difficulty=easy&type=multiple')

        assert response.status_code == 500
        assert b"Failed to fetch questions" in response.data

def test_fetch_questions_unexpected_error(client):
    """Test unexpected error during question fetching"""
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "results": [
                {
                    "question": "What is the capital of France?",
                    "correct_answer": "Paris",
                    "incorrect_answers": ["Lyon", "Marseille", "Toulouse"]
                }
            ]
        }

        with patch('app.models.Question.query.filter_by') as mock_query:
            mock_query.side_effect = Exception("Database error")

            response = client.get('/fetch_questions?category=9&difficulty=easy&type=multiple')

            assert response.status_code == 500
            assert b"An unexpected error occurred" in response.data

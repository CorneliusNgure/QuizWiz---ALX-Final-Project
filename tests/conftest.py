import pytest
from app import create_app
from config import TestingConfig

@pytest.fixture
def app():
    """Creates and configures a new Flask app instance for each test."""
    app = create_app()
    app.config.from_object(TestingConfig)

    with app.app_context():
        yield app  # test instance

@pytest.fixture
def client(app):
    """Provides a test client for making requests."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Provides a test CLI runner."""
    return app.test_cli_runner()

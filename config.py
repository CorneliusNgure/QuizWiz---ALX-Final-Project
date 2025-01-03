import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config(object):
    """Base configuration"""
    DEBUG = False
    TESTING = False

    DB_NAME = os.getenv("DB_NAME")
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")

    SESSION_COOKIE_SECURE = True

    @staticmethod
    def build_db_uri(username, password, host, port, db_name):
        """Builds the database URI from components"""
        return f"postgresql://{username}:{password}@{host}:{port}/{db_name}"

    DB_URI = build_db_uri(DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

    SQLALCHEMY_DATABASE_URI = DB_URI
    # Disable Flask-SQLAlchemy event system for performance reasons
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class ProductionConfig(Config):
    """Production-specific configuration"""
    pass

class DevelopmentConfig(Config):
    """Development-specific configuration"""
    DEBUG = True
    TESTING = True

    DB_NAME = "quizwiz_development_db"
    DB_URI = Config.build_db_uri(
        os.getenv("DB_USERNAME"),
        os.getenv("DB_PASSWORD"),
        os.getenv("DB_HOST"),
        os.getenv("DB_PORT"),
        DB_NAME
    )
    SESSION_COOKIE_SECURE = False

class TestingConfig(Config):
    """Testing-specific configuration"""
    TESTING = True
    DEBUG = True

    DB_NAME = "quizwiz_testing_db"
    DB_URI = Config.build_db_uri(
        os.getenv("DB_USERNAME"),
        os.getenv("DB_PASSWORD"),
        os.getenv("DB_HOST"),
        os.getenv("DB_PORT"),
        DB_NAME
    )
    SESSION_COOKIE_SECURE = False
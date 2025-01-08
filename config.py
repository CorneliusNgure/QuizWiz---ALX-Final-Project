import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config(object):
    """Base configuration"""
    DEBUG = False
    TESTING = False

    # Load database credentials
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def build_db_uri(username, password, host, port, db_name):
        """Builds the database URI from components"""
        return f"mysql+pymysql://{username}:{password}@{host}:{port}/{db_name}"

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        """Abstract method to ensure subclasses define the correct database"""
        raise NotImplementedError("Subclasses must define SQLALCHEMY_DATABASE_URI")


class DevelopmentConfig(Config):
    """Development-specific configuration"""
    DEBUG = True
    TESTING = True

    # Use environment-specific database name
    DB_NAME = os.getenv("DB_NAME_DEV")
    SQLALCHEMY_DATABASE_URI = Config.build_db_uri(
        Config.DB_USERNAME,
        Config.DB_PASSWORD,
        Config.DB_HOST,
        Config.DB_PORT,
        DB_NAME
    )
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing-specific configuration"""
    DEBUG = True
    TESTING = True

    # Use environment-specific database name
    DB_NAME = os.getenv("DB_NAME_TEST")
    SQLALCHEMY_DATABASE_URI = Config.build_db_uri(
        Config.DB_USERNAME,
        Config.DB_PASSWORD,
        Config.DB_HOST,
        Config.DB_PORT,
        DB_NAME
    )
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production-specific configuration"""
    # Use environment-specific database name
    DB_NAME = os.getenv("DB_NAME_PROD")
    SQLALCHEMY_DATABASE_URI = Config.build_db_uri(
        Config.DB_USERNAME,
        Config.DB_PASSWORD,
        Config.DB_HOST,
        Config.DB_PORT,
        DB_NAME
    )
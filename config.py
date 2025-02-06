import os
from dotenv import load_dotenv

# Loading environment variables from .env file
load_dotenv()

class Config(object):
    """Base configuration"""
    DEBUG = False
    TESTING = False

    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail Configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() in ["true", "1"]
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "False").lower() in ["true", "1"]
    MAIL_USERNAME = os.getenv("MAIL_USERNAME") 
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")  
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", MAIL_USERNAME)

    @staticmethod
    def build_db_uri(db_name):
        """Builds the database URI from environment variables"""
        username = os.getenv("DB_USERNAME")
        password = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST", "localhost")
        port = os.getenv("DB_PORT", "3306")
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
    SQLALCHEMY_DATABASE_URI = Config.build_db_uri(os.getenv("DB_NAME_DEV"))
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing-specific configuration"""
    DEBUG = True
    TESTING = True

    # Use environment-specific database name
    SQLALCHEMY_DATABASE_URI = Config.build_db_uri(os.getenv("DB_NAME_TEST"))
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production-specific configuration"""
    SQLALCHEMY_DATABASE_URI = Config.build_db_uri(os.getenv("DB_NAME_PROD"))

from flask import Flask
from config import DevelopmentConfig, ProductionConfig, TestingConfig
import os
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, upgrade
from flask_mail import Mail  # Import Flask-Mail
from dotenv import load_dotenv

# Loading environment variables from .env
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()  # Initialize mail instance

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)

    ENV = os.getenv("FLASK_ENV", "development").lower()
    print(f"Current environment: {ENV}")

    # Configuration mapping
    ENV_CONFIGS = {
        "production": ProductionConfig,
        "testing": TestingConfig,
        "development": DevelopmentConfig,
    }

    # Applying the corresponding configuration
    app.config.from_object(ENV_CONFIGS.get(ENV, DevelopmentConfig))
    app.debug = app.config["DEBUG"]

    if not os.getenv("FLASK_ENV"):
        app.logger.warning("FLASK_ENV not set, defaulting to 'development'")

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")

    # Initialization of extensions
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)  # Initialize Flask-Mail

    # Logging levels
    if ENV == "development":
        app.logger.setLevel(logging.DEBUG)
    elif ENV == "testing":
        app.logger.setLevel(logging.WARNING)
    else:
        app.logger.setLevel(logging.INFO)

    app.logger.info(f"Current configuration: {ENV}")

    # Registration of blueprints
    with app.app_context():
        try:
            from app.routes import main_bp
            app.register_blueprint(main_bp)
        except ImportError as e:
            app.logger.error(f"Error importing blueprint: {e}")

        # Apply migrations conditionally
        if ENV in ["development", "testing"]:
            try:
                upgrade()
                app.logger.info("Database migrations applied.")
            except Exception as e:
                app.logger.error(f"Error applying migrations: {e}")

    return app
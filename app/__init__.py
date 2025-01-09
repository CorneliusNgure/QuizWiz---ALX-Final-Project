from flask import Flask
from config import DevelopmentConfig, ProductionConfig, TestingConfig
import os
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv


load_dotenv()

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)

    ENV = os.getenv("FLASK_ENV", "development").lower()

    # configuration mapping
    ENV_CONFIGS = {
        "production": ProductionConfig,
        "testing": TestingConfig,
        "development": DevelopmentConfig,
    }

    # applying the corresponding configuration
    app.config.from_object(ENV_CONFIGS.get(ENV, DevelopmentConfig))
    app.debug = app.config['DEBUG']

    # warning if FLASK_ENV is not set
    if not os.getenv("FLASK_ENV"):
        app.logger.warning("FLASK_ENV not set, defaulting to 'development'")

    # setting the SECRET_KEY
    app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")

    # Initialization of extensions
    db.init_app(app)
    migrate.init_app(app, db)

    app.logger.setLevel(logging.INFO)
    app.logger.info(f"Current configuration: {ENV}")

    # registeration of blueprints
    with app.app_context():
        try:
            from app.routes import main_bp
            app.register_blueprint(main_bp)

            # Automatically create tables only for development or testing
            if ENV in ["development", "testing"]:
                db.create_all()
                app.logger.info("Tables created automatically in development/testing.")
        except ImportError as e:
            app.logger.error(f"Error importing blueprint: {e}")
    
    return app
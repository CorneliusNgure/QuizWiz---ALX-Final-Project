from flask import Flask
from config import DevelopmentConfig, ProductionConfig, TestingConfig
import os
import logging
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)

ENV = os.getenv("FLASK_ENV", "development").lower()

ENV_CONFIGS = {
    "production": ProductionConfig,
    "testing": TestingConfig,
    "development": DevelopmentConfig,
}

app.config.from_object(ENV_CONFIGS.get(ENV, DevelopmentConfig))


app.debug = app.config['DEBUG']

logging.basicConfig(level=logging.INFO)
app.logger.info(f"Current configuration: {ENV}")

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
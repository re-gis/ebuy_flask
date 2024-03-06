from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from src.config.config import Config
from dotenv import load_dotenv
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt


load_dotenv()

app = Flask(__name__)
config = Config().dev_config
app.env = config.ENV
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI_DEV")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv(
    "SQLALCHEMY_TRACK_MODIFICATIONS"
)
db = SQLAlchemy(app=app)
migrate = Migrate(app=app, db=db)

from src.routes import api

app.register_blueprint(api, url_prefix="/api")
from src.models.user_model import Users

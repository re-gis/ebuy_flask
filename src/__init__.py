from flask import Flask
from flask_mail import Mail
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
app.config["MAIL_SERVER"] = os.getenv("MAIL_SERVER")
app.config["MAIL_PORT"] = os.getenv("MAIL_PORT")
app.config["MAIL_USE_TLS"] = os.getenv("MAIL_USE_TLS")
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME")  # Your Gmail email address
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD")
db = SQLAlchemy(app=app)
migrate = Migrate(app=app, db=db)
mail = Mail(app)

from src.routes import api

app.register_blueprint(api, url_prefix="/api")
from src.models.models import Users

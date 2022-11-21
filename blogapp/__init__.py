import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from os import path
if path.exists("env.py"):
    import env
from flask_mail import Mail

# create the app
app = Flask(__name__)

csrf = CSRFProtect(app)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

# accept requests that are up to 1MB in size
# app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024

# only accepts jpg and png file extensions
app.config["UPLOAD_EXTENSIONS"] = [".jpg", ".png"]

# upload pictures
app.config["UPLOAD_PATH"] = "blogapp/static/uploads"

# create the extension
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

csrf = CSRFProtect(app)

# initialize the app with the extension
db.init_app(app)

app.config["MAIL_SERVER"] = "smtp.googlemail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("EMAIL_USER")
app.config["MAIL_PASSWORD"] = os.environ.get("EMAIL_PASS")
app.config["SECURITY_PASSWORD_SALT"] = os.environ.get("SECURITY_PASSWORD_SALT")
mail = Mail(app)

from blogapp import user_routes, post_routes
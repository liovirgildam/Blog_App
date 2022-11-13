import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from os import path
if path.exists("env.py"):
    import env


# create the app
app = Flask(__name__)

csrf = CSRFProtect(app)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

# accept requests that are up to 1MB in size
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024

# only accepts jpg and png file extensions
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png']

# upload pictures
app.config['UPLOAD_PATH'] = 'blogapp/static/uploads'

# create the extension
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

csrf = CSRFProtect(app)

# initialize the app with the extension
db.init_app(app)

from blogapp import routes
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from os import path
if path.exists("env.py"):
    import env

# create the app
app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") 

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

# create the extension 
db = SQLAlchemy()

# initialize the app with the extension
db.init_app(app)

@app.route("/")
def homepage():
    return "<h1>Homepage</h1>"
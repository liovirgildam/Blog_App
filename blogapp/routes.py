from flask import render_template
from blogapp import app
from blogapp.models import User, Post

@app.route("/")
def homepage():
    return render_template("homepage.html")
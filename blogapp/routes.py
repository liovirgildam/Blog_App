from flask import render_template, request, redirect, url_for
from blogapp import app
from blogapp.models import User, Post

@app.route("/")
def homepage():
    return render_template("homepage.html", title="Blog Homepage")

@app.route("/login", methods = ['GET','POST'])
def login():
    return render_template("login.html", title="login")

@app.route("/signup", methods = ['GET','POST'])
def signup():
    if request.method == "POST":
        return redirect(url_for('homepage'))
    return render_template("signup.html", title="login")
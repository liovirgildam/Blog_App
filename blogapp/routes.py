from flask import render_template, request, redirect, url_for, flash
from blogapp import app, db, bcrypt
from blogapp.models import User, Post
import sqlite3
from sqlite3 import IntegrityError

@app.route("/")
def homepage():
    return render_template("homepage.html", title="Blog Homepage")

@app.route("/login", methods = ['GET','POST'])
def login():
    return render_template("login.html", title="login")

@app.route("/signup", methods = ['GET','POST'])
def signup():
    if request.method == "POST":
        usernameExist = db.session.execute(db.select(User).where(User.username == request.form["username"] )).scalar()
        if usernameExist:
            flash("Username already exists")
        else:
            emailExist = db.session.execute(db.select(User).where(User.email == request.form["email"] )).scalar()
            if emailExist:
                flash("Email already exists")
            else:
                user = User(
                    name = request.form["name"],
                    username = request.form["username"],
                    email = request.form["email"],
                    password = bcrypt.generate_password_hash(request.form["password"]).decode('utf-8')
                )
                db.session.add(user)
                db.session.commit() 
                return redirect(url_for('homepage', id=user.id))
    return render_template("signup.html", title="login")
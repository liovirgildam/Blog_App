import os
from os import path
if path.exists("env.py"):
    import env
from flask import (flash, redirect, render_template, request, session, url_for)
from PIL import Image
from werkzeug.utils import secure_filename
from blogapp import app, bcrypt, db, mail
from blogapp.models import User, Post
from flask_mail import Message
from blogapp.routes_methods import (set_session, remove_session, save_picture, send_reset_email, news_api)
import requests

# Homepage route
@app.route("/")
def homepage():
    news = news_api()
    posts = db.session.execute(db.select(Post).order_by(Post.postedOn.desc())).scalars()
    return render_template("homepage.html", title="Blog Homepage", posts = posts, news = news)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        # Queries the database to find an user with a specific email
        userExists =  db.session.execute(db.select(User).where(
            User.email == request.form["email"])).scalar()
        if userExists:
            userPassword = db.session.execute(db.select(User.password).where(
                User.email == request.form["email"])).scalar()
            formPassword = request.form["password"]

            # Checks if user introduced a valid password
            if bcrypt.check_password_hash(userPassword, formPassword):
                user = db.session.execute(db.select(User).where(
                    User.email == request.form["email"])).scalar()
                
                # Adds user details to session
                set_session(user)
                return  redirect(url_for("homepage"))
        flash("Email or password invalid, please try again.", "danger")
    return render_template("login.html", title="login")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        if request.form["password"] != request.form["confPassword"]:
            flash("Passwords don't match", "danger")
        else:
            # Checks if username already taken
            usernameExist = db.session.execute(db.select(User).where(
                User.username == request.form["username"].lower())).scalar()
            if usernameExist:
                flash("Username not available","danger")
            else:

                # Checks if user has already an account with that email
                emailExist = db.session.execute(db.select(User).where(
                    User.email == request.form["email"])).scalar()
                if emailExist:
                    flash("Email already exists", "danger")
                else:

                    # Creates a new user account
                    user = User(
                        name=request.form["name"],
                        username=request.form["username"].lower(),
                        email=request.form["email"],
                        password=bcrypt.generate_password_hash(
                            request.form["password"]).decode("utf-8")
                    )
                    db.session.add(user)
                    db.session.commit()
                    set_session(user)
                    return redirect(url_for("homepage"))
    return render_template("sign_up.html", title="signup")

# route to posts by specific user
@app.route("/user/<int:id>")
def user_posts(id):
    posts = db.session.execute(db.select(Post).where(
            Post.user_id == id).order_by(Post.postedOn.desc())).scalars()
    news = news_api()
    return render_template("posts.html", title="Blog Homepage", posts = posts, news = news)

# Removes user details from session
@app.route("/logout")
def logout():
    remove_session()
    return redirect(url_for("homepage"))

# Renders account page
@app.route("/account")
def account():
    return render_template("account.html")

# Allows user to upload a profile picture 
@app.route("/upload_file", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        profile_pic = request.files["profile_picture"]
        # Returns a secure filename
        filename = secure_filename(profile_pic.filename)
        if filename == "": 
            flash("Please upload a picture with a valid name","warning")
            return redirect(url_for("account"))

        # Removes previous profile picture from folder
        if session["profile_picture"] != "default.jpeg":
            os.remove(f"blogapp/static/uploads/{session['profile_picture']}")
        
        # saves picture to folder and returns filename
        picture_name = save_picture(profile_pic, filename)

        # saves filename to database
        db.session.execute(db.update(User).values(profile_picture = picture_name ).where(
            User.id == session["user_id"]))
        db.session.commit()

        # updates session with new profile picture details
        session["profile_picture"] = picture_name
        return redirect(url_for('account'))
    return render_template("account.html")
    
# Updates user details in the database
@app.route("/update", methods=["GET","POST"])
def update_details():
    if request.method == "POST":
        # If user doesn't update name or username, it flashes an error message
        if request.form["name"] == "" and request.form["username"] == "":
            flash("Please provide name/username", "danger")
            return redirect(url_for("account"))
        
        # updates the name
        elif request.form["username"] == "":
            db.session.execute(db.update(User).values(name = request.form["name"]).where(
            User.id == session["user_id"]))
            session["name"] = request.form["name"]
        elif request.form["name"] == "":
            # Updates username if not taken
            usernameExist = db.session.execute(db.select(User).where(
                User.username == request.form["username"].lower())).scalar()
            if usernameExist:
                flash("Username not available","danger")
            else:
                db.session.execute(db.update(User).values(username = request.form["username"].lower()).where(
                    User.id == session["user_id"]))
                session["username"] = request.form["username"]
        else:
            # updates name and username in database
            db.session.execute(db.update(User).values(name = request.form["name"], 
                username = request.form["username"].lower()).where(
                User.id == session["user_id"]))
            session["name"] = request.form["name"] 
            session["username"] = request.form["username"]

        # Adds changes to databse and redirects to account page
        db.session.commit()
        return redirect(url_for("account"))   
    return render_template("account.html")

# route to reset password email form
@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if request.method == "POST":
        user =  db.session.execute(db.select(User).where(User.email == request.form["email"])).scalar()
        if user:
            send_reset_email(user)
            flash("An email with instructions have been sent.","success")      
            return redirect(url_for("login"))
        # flashes an error if there isn't an user with that account
        flash("Invalid email","danger")
    return render_template("reset_request.html", title = "Reset Password")

# route to reset password from email
@app.route("/reset_password/<token>", methods =["GET", "POST"])
def reset_token(token):
    # verify_reset_token checks if the token is valid and returns an user if it is
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token","danger")
        return redirect(url_for("reset_request"))
    
    if request.method == "POST":
        # it flashes an error if passwords don't match
        if request.form["password"] != request.form["confPassword"]:
            flash("Passwords don't match","danger")
            return redirect(url_for("reset_request"))
        else:
            # Encrypts password and saves it to database
            password=bcrypt.generate_password_hash(
                    request.form["password"]).decode("utf-8")
            user.password = password
            db.session.commit()
            flash("Your password has been updated! You can now login.","success")
            return redirect(url_for("login"))
    return render_template("reset_token.html", title = "Reset Password")



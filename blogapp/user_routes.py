import os
from flask import (flash, redirect, render_template, request, session, url_for)
from PIL import Image
from werkzeug.utils import secure_filename
from blogapp import app, bcrypt, db, mail
from blogapp.models import User, Post
from flask_mail import Message

def set_session(user_details):
    session["user_id"] = user_details.id
    session["name"] = user_details.name  
    session["username"] = user_details.username
    session["profile_picture"] = user_details.profile_picture
    return None

def remove_session():
    session.pop('user_id', None)
    session.pop('name', None)
    session.pop('username', None)
    session.pop('profile_picture', None)
    return None

def thumbnail_profile_picture(profile_pic):
    output_size = (200, 200)
    profile = Image.open(profile_pic)
    profile.thumbnail(output_size)
    return profile

def save_picture(profile_pic, filename):
    file_ext = os.path.splitext(filename)[1]
    new_filename = str(session["user_id"])+ file_ext
    picture = thumbnail_profile_picture(profile_pic)
    picture.save(os.path.join(app.config["UPLOAD_PATH"], new_filename))
    return new_filename

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', 
                sender='no.reply.mendonca@gmail.com',
                recipients = [user.email])
    msg.body =f'''To reset your password, visit the following link:
{url_for('reset_token', token = token, _external=True)}
If you don't receive this email in one minute, please check spam folder.
If you didn't request this, please ignore this email.  
'''
    mail.send(msg)

# App routes

# Homepage route
@app.route("/")
def homepage():
    posts = db.session.execute(db.select(Post).order_by(Post.postedOn.desc())).scalars()
    return render_template("homepage.html", title="Blog Homepage", posts = posts)

@app.route("/login", methods=['GET', 'POST'])
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
                return  redirect(url_for('homepage'))
        flash("Email or password invalid, please try again.")
    return render_template("login.html", title="login")

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        if request.form["password"] != request.form["confPassword"]:
            flash("Passwords don't match")
        else:
            # Checks if username already taken
            usernameExist = db.session.execute(db.select(User).where(
                User.username == request.form["username"].lower())).scalar()
            if usernameExist:
                flash("Username not available")
            else:

                # Checks if user has already an account with that email
                emailExist = db.session.execute(db.select(User).where(
                    User.email == request.form["email"])).scalar()
                if emailExist:
                    flash("Email already exists")
                else:

                    # Creates a new user account
                    user = User(
                        name=request.form["name"],
                        username=request.form["username"].lower(),
                        email=request.form["email"],
                        password=bcrypt.generate_password_hash(
                            request.form["password"]).decode('utf-8')
                    )
                    db.session.add(user)
                    db.session.commit()
                    set_session(user)
                    return redirect(url_for('homepage'))
    return render_template("sign_up.html", title="signup")

# route to posts by specific user
@app.route("/user/<int:id>")
def user_posts(id):
    posts = db.session.execute(db.select(Post).where(
            Post.user_id == id).order_by(Post.postedOn.desc())).scalars()
    return render_template("posts.html", title="Blog Homepage", posts = posts)

# Removes user details from session
@app.route("/logout")
def logout():
    remove_session()
    return redirect(url_for('homepage'))

# Renders account page
@app.route("/account")
def account():
    return render_template("account.html")

# Allows user to upload a profile picture 
@app.route("/upload_file", methods=['GET', 'POST'])
def upload_file():
    if request.method == "POST":
        profile_pic = request.files['profile_picture']
        # Returns a secure filename
        filename = secure_filename(profile_pic.filename)
        if filename == '': 
            flash('Please upload a picture with a valid name')
            return redirect(url_for('account'))

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
@app.route("/update", methods=['GET','POST'])
def update_details():
    if request.method == "POST":
        # If user doesn't update name or username, it flashes an error message
        if request.form["name"] == "" and request.form["username"] == "":
            flash("Please provide name/username")
            return redirect(url_for('account'))
        
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
                flash("Username not available")
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
        return redirect(url_for('account'))   
    return render_template("account.html")

# route to reset password email form
@app.route("/reset_password", methods=['GET','POST'])
def reset_request():
    if request.method == 'POST':
        user =  db.session.execute(db.select(User).where(User.email == request.form["email"])).scalar()
        if user:
            send_reset_email(user)
            flash("An email with instructions have been sent.")      
            return redirect(url_for('login'))
        # flashes an error if there isn't an user with that account
        flash("Invalid email")
    return render_template('reset_request.html', title = 'Reset Password')

# route to reset password from email
@app.route("/reset_password/<token>", methods =['GET', 'POST'])
def reset_token(token):
    # verify_reset_token checks if the token is valid and returns an user if it is
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token')
        return redirect(url_for('reset_request'))
    
    if request.method == 'POST':
        # it flashes an error if passwords don't match
        if request.form["password"] != request.form["confPassword"]:
            flash("Passwords don't match")
            return redirect(url_for('reset_request'))
        else:
            # Encrypts password and saves it to database
            password=bcrypt.generate_password_hash(
                    request.form["password"]).decode('utf-8')
            user.password = password
            db.session.commit()
            flash('Your password has been updated! You can now login.')
            return redirect(url_for('login'))
    return render_template("reset_token.html", title = 'Reset Password')



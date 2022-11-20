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

@app.route("/")
def homepage():
    posts = db.session.execute(db.select(Post).order_by(Post.postedOn.desc())).scalars()
    return render_template("homepage.html", title="Blog Homepage", posts = posts)

@app.route("/<int:id>")
def user_posts(id):
    posts = db.session.execute(db.select(Post).where(
            Post.user_id == id).order_by(Post.postedOn.desc())).scalars()
    return render_template("posts.html", title="Blog Homepage", posts = posts)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        userExists =  db.session.execute(db.select(User).where(
            User.email == request.form["email"])).scalar()
        if userExists:
            userPassword = db.session.execute(db.select(User.password).where(
                User.email == request.form["email"])).scalar()
            formPassword = request.form["password"]

            if bcrypt.check_password_hash(userPassword, formPassword):
                user = db.session.execute(db.select(User).where(
                    User.email == request.form["email"])).scalar()
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
            usernameExist = db.session.execute(db.select(User).where(
                User.username == request.form["username"].lower())).scalar()
            if usernameExist:
                flash("Username not available")
            else:
                emailExist = db.session.execute(db.select(User).where(
                    User.email == request.form["email"])).scalar()
                if emailExist:
                    flash("Email already exists")
                else:
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


@app.route("/logout")
def logout():
    session.pop('user_id', None)
    session.pop('name', None)
    session.pop('username', None)
    session.pop('profile_picture', None)
    return redirect(url_for('homepage'))


@app.route("/account")
def account():
    return render_template("account.html")

@app.route("/upload_file", methods=['GET', 'POST'])
def upload_file():
    if request.method == "POST":
        profile_pic = request.files['profile_picture']
        filename = secure_filename(profile_pic.filename)
        if session["profile_picture"] != "default.jpeg":
            os.remove(f"blogapp/static/uploads/{session['profile_picture']}")
        file_ext = os.path.splitext(filename)[1]
        new_filename = str(session["user_id"])+ file_ext
        output_size = (200, 200)
        profile = Image.open(profile_pic)
        profile.thumbnail(output_size)
        profile.save(os.path.join(app.config["UPLOAD_PATH"], new_filename))
        db.session.execute(db.update(User).values(profile_picture = new_filename).where(
            User.id == session["user_id"]))
        db.session.commit()
        session["profile_picture"] = new_filename
        return redirect(url_for('account'))
    return render_template("account.html")
    

@app.route("/update", methods=['GET','POST'])
def update_details():
    if request.method == "POST":
        if request.form["name"] == '' and request.form["username"] == '':
            flash("Please provide name/username")
            return redirect(url_for('account'))
        elif request.form["username"] == '':
            db.session.execute(db.update(User).values(name = request.form["name"]).where(
            User.id == session["user_id"]))
            db.session.commit()
            session["name"] = request.form["name"]
        else:
            usernameExist = db.session.execute(db.select(User).where(
                User.username == request.form["username"].lower())).scalar()
            if usernameExist:
                flash("Username not available")
            else:
                db.session.execute(db.update(User).values(username = request.form["username"].lower()).where(
                    User.id == session["user_id"]))
                db.session.commit()
                session["username"] = request.form["username"]
        return redirect(url_for('account'))
    return render_template("account.html")

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', 
                sender='no.reply.mendonca@gmail.com',
                recipients = [user.email])
    msg.body =f'''To reset your password, visit the following link:
{url_for('reset_token', token = token, _external=True)}
If you didn't request this, please ignore this email.  
'''
    mail.send(msg)

@app.route("/reset_password", methods=['GET','POST'])
def reset_request():
    if request.method == 'POST':
        user =  db.session.execute(db.select(User).where(User.email == request.form["email"])).scalar()
        send_reset_email(user)
        flash("An email with instructions have been sent.")      
        return redirect(url_for('login'))
    return render_template('reset_request.html', title = 'Reset Password')

@app.route("/reset_password/<token>", methods =['GET', 'POST'])
def reset_token(token):
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token')
        return redirect(url_for('reset_request'))
    if request.method == 'POST':
        if request.form["password"] != request.form["confPassword"]:
            flash("Passwords don't match")
            return redirect(url_for('reset_request'))
        else:
            password=bcrypt.generate_password_hash(
                    request.form["password"]).decode('utf-8')
            user.password = password
            db.session.commit()
            flash('Your password has been updated! You can now login.')
            return redirect(url_for('login'))
    return render_template("reset_token.html", title = 'Reset Password')


@app.route("/post", methods=['GET', 'POST'])
def post():
    if request.method == "POST":
        post = Post(
            title = request.form["title"],
            text = request.form["post"],
            user_id = session["user_id"],
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('homepage'))
    return render_template("homepage.html", title="Homepage")

@app.route("/newpost")
def newpost():
    return render_template("new_post.html", title="New post")

@app.route("/post/<int:id>")
def singlepost(id):
    post = db.session.execute(db.select(Post).where(
            Post.id == id)).scalar()
    return render_template("post.html", post = post)

@app.route("/delete/post/<int:id>", methods=['GET','POST'])
def delete_post(id): 
    db.session.execute(db.delete(Post).where(Post.id == id))
    db.session.commit()
    flash("Post deleted")
    return redirect(url_for('homepage'))

@app.route("/post/updateform/<int:id>", methods=['GET', 'POST'])
def updateform(id):
    post = db.session.execute(db.select(Post).where(Post.id == id)).scalar()
    return render_template("update_post.html", post= post)

@app.route("/update/post/<int:id>", methods = ['GET','POST'])
def updatepost(id):
    if request.method == 'POST':
        if request.form['title'] =='' and request.form['post']== '':
            return redirect(url_for('singlepost', id = id))
        elif request.form['title'] == '':
            db.session.execute(db.update(Post).values(text = request.form["post"]).where(Post.id == id))
        elif request.form['post'] == '':
            db.session.execute(db.update(Post).values(title = request.form["title"]).where(Post.id == id))
        else:
            db.session.execute(db.update(Post).values(title = request.form["title"],text = request.form["post"] ).where(Post.id == id))
        db.session.commit()  
        return redirect(url_for('singlepost', id = id))
    return redirect(url_for('updateform', id = id))


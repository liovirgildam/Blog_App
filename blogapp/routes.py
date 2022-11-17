import os
from flask import (flash, redirect, render_template, request, session, url_for)
from PIL import Image
from werkzeug.utils import secure_filename

from blogapp import app, bcrypt, db
from blogapp.models import User, Post


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
    return render_template("signup.html", title="signup")


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
    return render_template("newpost.html", title="New post")

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
    return render_template("updatepost.html", post= post)

@app.route("/update/post/<int:id>", methods = ['GET','POST'])
def updatepost(id):
    if request.method == 'POST':
        if request.form['title'] =='' and request.form['post']== '':
            return redirect(url_for('singlepost', id = id))
        elif request.form['title'] == '':
            db.session.execute(db.update(Post).values(text = request.form["post"]).where(Post.id == id))
            db.session.commit()
        elif request.form['post'] == '':
            db.session.execute(db.update(Post).values(title = request.form["title"]).where(Post.id == id))
            db.session.commit()
        else:
            db.session.execute(db.update(Post).values(title = request.form["title"],text = request.form["post"] ).where(Post.id == id))
            db.session.commit()
        return redirect(url_for('singlepost', id = id))
    return redirect(url_for('updateform', id = id))
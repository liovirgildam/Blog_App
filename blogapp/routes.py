from flask import render_template, request, redirect, url_for, flash, session
from blogapp import app, db, bcrypt
from blogapp.models import User


@app.route("/")
def homepage():
    return render_template("homepage.html", title="Blog Homepage")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        userPassword = db.session.execute(db.select(User.password).where(
            User.email == request.form["email"])).scalar()
        formPassword = request.form["password"]

        if bcrypt.check_password_hash(userPassword, formPassword):
            username = db.session.execute(db.select(User.username).where(
                User.email == request.form["email"])).scalar()
            session["username"] = username
            return render_template("homepage.html", title="Homepage")
        else:
            flash("Email or password invalid, please try again.")
    return render_template("login.html", title="login")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        if request.form["password"] != request.form["confPassword"]:
            flash("Passwords don't match")
        else:
            usernameExist = db.session.execute(db.select(User).where(
                User.username == request.form["username"])).scalar()
            if usernameExist:
                flash("Username already exists")
            else:
                emailExist = db.session.execute(db.select(User).where(
                    User.email == request.form["email"])).scalar()
                if emailExist:
                    flash("Email already exists")
                else:
                    user = User(
                        name=request.form["name"],
                        username=request.form["username"],
                        email=request.form["email"],
                        password=bcrypt.generate_password_hash(
                            request.form["password"]).decode('utf-8')
                    )
                    db.session.add(user)
                    db.session.commit()
                    session[user] = user
                    return redirect(url_for('homepage', id=user.id))
    return render_template("signup.html", title="signup")


@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('homepage'))

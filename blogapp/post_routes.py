from flask import (flash, redirect, render_template, request, session, url_for)
from blogapp import app, db
from blogapp.models import Post

# Add a new post to database
@app.route("/post", methods=["GET", "POST"])
def post():
    if request.method == "POST":
        post = Post(
            title = request.form["title"],
            text = request.form["post"],
            user_id = session["user_id"],
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for("homepage"))
    return render_template("homepage.html", title="Homepage")

# Shows a page with new post form 
@app.route("/newpost")
def new_post():
    return render_template("new_post.html", title="New post")

# Shows a page with a single post
@app.route("/post/<int:id>")
def single_post(id):
    post = db.session.execute(db.select(Post).where(
            Post.id == id)).scalar()
    return render_template("post.html", post = post)

# Deletes a post
@app.route("/delete/post/<int:id>", methods=["GET","POST"])
def delete_post(id): 
    db.session.execute(db.delete(Post).where(Post.id == id))
    db.session.commit()
    flash("Post deleted", "warning")
    return redirect(url_for("homepage"))

# Shows a page to update a post
@app.route("/updateform/post/<int:id>", methods=["GET", "POST"])
def update_form(id):
    post = db.session.execute(db.select(Post).where(Post.id == id)).scalar()
    return render_template("update_post.html", post= post)

# Updates post in database
@app.route("/update/post/<int:id>", methods =["GET", "POST"])
def update_post(id):
    if request.method == "POST":
        if request.form["title"] =="" and request.form["post"]== "":
            return redirect(url_for("single_post", id = id))
        elif request.form["title"] == "":
            db.session.execute(db.update(Post).values(text = request.form["post"]).where(Post.id == id))
        elif request.form["post"] == "":
            db.session.execute(db.update(Post).values(title = request.form["title"]).where(Post.id == id))
        else:
            db.session.execute(db.update(Post).values(title = request.form["title"],text = request.form["post"] ).where(Post.id == id))
        db.session.commit()  
        return redirect(url_for("single_post", id = id))
    return redirect(url_for("update_form", id = id))


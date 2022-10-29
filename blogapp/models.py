from datetime import datetime
from blogapp import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)
    profile_picture = db.Column(db.String, nullable=False, default='default.jpg')
    summary = db.Column(db.String)
    posts = db.relationship('Peeps', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.name}','{self.username}','{self.profile_picture}','{self.summary}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    postedOn = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    text = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.postedOn}')"
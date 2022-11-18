from datetime import datetime
from blogapp import app, db
from itsdangerous.url_safe import URLSafeSerializer as Serializer

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)
    profile_picture = db.Column(db.String, nullable=False, default='default.jpeg')
    summary = db.Column(db.String)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        return  s.dumps(self.id)

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)
        except:
            return None
        return User.query.get(user_id)

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


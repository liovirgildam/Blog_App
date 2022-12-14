from datetime import datetime
from blogapp import app, db
from itsdangerous.url_safe import URLSafeSerializer as Serializer

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String(40), nullable=False)
    profile_picture = db.Column(db.String, nullable=False, default="default.jpeg")
    summary = db.Column(db.String)
    posts = db.relationship("Post", backref="author", lazy=True)

    # Creates a token that is send to the user's email to reset its password
    def get_reset_token(self):
        s = Serializer(app.config["SECRET_KEY"])
        return  s.dumps({ "user_id": self.id},  salt=app.config["SECURITY_PASSWORD_SALT"])

    # Checks if token is valid or not, returns user details if valid
    @staticmethod
    def verify_reset_token(token, expiration=3600):
        s = Serializer(app.config["SECRET_KEY"])
        try:
            user_id = s.loads(token, 
            salt=app.config["SECURITY_PASSWORD_SALT"],
            max_age=expiration)["user_id"]
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
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.postedOn}')"


import os
from os import path
if path.exists("env.py"):
    import env
from flask import  session, url_for
from PIL import Image
from blogapp import app, mail
from flask_mail import Message
import requests

def set_session(user_details):
    session["user_id"] = user_details.id
    session["name"] = user_details.name  
    session["username"] = user_details.username
    session["profile_picture"] = user_details.profile_picture
    return None

def remove_session():
    session.pop("user_id", None)
    session.pop("name", None)
    session.pop("username", None)
    session.pop("profile_picture", None)
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
    msg = Message("Password Reset Request", 
                sender="no.reply.mendonca@gmail.com",
                recipients = [user.email])
    msg.body =f'''To reset your password, visit the following link:
{url_for("reset_token", token = token, _external=True)}
If you don't receive this email in one minute, please check spam folder.
If you didn't request this, please ignore this email.  
'''
    mail.send(msg)

def news_api():
    news = []
    response_api = requests.get(f"https://newsdata.io/api/1/news?apikey={os.environ['API_KEY']}&q=tech&language=en&category=business,technology,top ")
    if response_api.status_code == 200:
        data = response_api.json()["results"]
        for article in range(5):
            news.append({"title":data[article]["title"] , "link": data[article]["link"]})
        return news
    return None
from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}>'.format(self.username)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    body = db.Column(db.Text)
    image_filename = db.Column(db.String(140)) # Keeping for backward compatibility or cover image
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    photos = db.relationship('Photo', backref='post', lazy='dynamic')

    def __repr__(self):
        return '<Post {}>'.format(self.title)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(140))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    
    # Metadata
    date_taken = db.Column(db.DateTime)
    location = db.Column(db.String(200))
    camera_make = db.Column(db.String(100))
    camera_model = db.Column(db.String(100))
    lens = db.Column(db.String(100))
    focal_length = db.Column(db.String(50))
    aperture = db.Column(db.String(50))
    shutter_speed = db.Column(db.String(50))
    iso = db.Column(db.String(50))

    def __repr__(self):
        return '<Photo {}>'.format(self.image_filename)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_filename = db.Column(db.String(140))
    bio = db.Column(db.Text)
    
    # Social Links
    email = db.Column(db.String(120))
    website = db.Column(db.String(120))
    instagram = db.Column(db.String(120))
    facebook = db.Column(db.String(120))
    threads = db.Column(db.String(120))
    bluesky = db.Column(db.String(120))
    mastodon = db.Column(db.String(120))
    x = db.Column(db.String(120))
    linkedin = db.Column(db.String(120))
    youtube = db.Column(db.String(120))
    tiktok = db.Column(db.String(120))
    kofi = db.Column(db.String(120))

    def __repr__(self):
        return '<Profile {}>'.format(self.id)

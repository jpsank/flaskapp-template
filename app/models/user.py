from datetime import datetime
from hashlib import md5
from time import time
from flask import current_app, escape
from sqlalchemy import func
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

from app import db, login
from app.util.helpers import nl2br
from .base import Base
from .vote import Vote
from .sub import Sub
from .post import Post


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, Base):

    id = db.Column(db.Integer, primary_key=True)

    # User authentication information
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    # User email information
    email = db.Column(db.String(300), nullable=False, unique=True)
    confirmed_at = db.Column(db.DateTime())

    # User information
    about_me = db.Column(db.String(300))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    votes = db.relationship('Vote', backref='user', lazy='dynamic')
    chats = db.relationship('Chat', backref='creator', lazy='dynamic')

    subscriptions = db.relationship(
        'Chat', secondary='sub',
        backref=db.backref('subscribers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def score(self):
        score = 0
        for post in self.posts:
            score += post.score()
        return score

    @property
    def about_me_e(self):
        return nl2br(str(escape(self.about_me)))

    # Voting

    def upvote(self, post):
        existing = self.already_voted(post)
        if existing is not None:
            existing.liked = True
            return existing
        else:
            return Vote(user_id=self.id, post_id=post.id, liked=True)

    def downvote(self, post):
        existing = self.already_voted(post)
        if existing is not None:
            existing.liked = False
            return existing
        else:
            return Vote(user_id=self.id, post_id=post.id, liked=False)

    def already_voted(self, post):
        return self.votes.filter(Vote.post_id == post.id).first()

    # Subscriptions

    def subscribe(self, chat):
        if not self.is_subscribed(chat):
            self.subscriptions.append(chat)

    def unsubscribe(self, chat):
        if self.is_subscribed(chat):
            self.subscriptions.remove(chat)

    def is_subscribed(self, chat):
        return self.subscriptions.filter(
            Sub.chat_id == chat.id).scalar() is not None

    def subscribed_posts(self):
        return Post.query.join(Sub, (Sub.chat_id == Post.chat_id))\
            .filter(Sub.user_id == self.id)

    # Authentication

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'],
            algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    # Custom queries

    @staticmethod
    def get_by_username(username):
        return User.query.filter(func.lower(User.username) == func.lower(username)).first()

    @staticmethod
    def get_by_email(email):
        return User.query.filter(func.lower(User.email) == func.lower(email)).first()

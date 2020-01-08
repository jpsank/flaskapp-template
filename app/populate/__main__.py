from flask import current_app
import json
import os

from app import db
from app.models import User, Chat, Post, Comment, Vote
from config import basedir


# USERS
def create_user(fake_user):
    user = User(username=fake_user["username"], email=fake_user["email"])
    user.set_password(fake_user["password"])
    return user


# CHATS
def create_chat(fake_chat):
    chat = Chat(name=fake_chat["name"])
    chat.creator = User.get_by_username(fake_chat["creator"])
    return chat


# COMMENTS
def create_comments(fake_comments, parent_post=None, parent_comment=None):
    for fake_comment in fake_comments:
        comment = Comment(body=fake_comment["body"])
        if parent_post is not None:
            comment.post = parent_post
        if parent_comment is not None:
            comment.parent_comment = parent_comment
        comment.author = User.get_by_username(fake_comment["author"])
        if "comments" in fake_comment:
            create_comments(fake_comment["comments"], parent_comment=comment)


# POSTS
def create_post(fake_post):
    post = Post(title=fake_post["title"], body=fake_post["body"])
    post.chat = Chat.get_by_name(fake_post["chat"])
    post.author = User.get_by_username(fake_post["author"])
    if "comments" in fake_post:
        create_comments(fake_post["comments"], parent_post=post)


if __name__ == '__main__':
    with open(os.path.join(basedir, "app/populate/fake_users.json"), "r") as f:
        fake_users = json.load(f)
    for fake_user in fake_users:
        db.session.add(create_user(fake_user))
    db.session.commit()

    with open(os.path.join(basedir, "app/populate/fake_chats.json"), "r") as f:
        fake_chats = json.load(f)
    for fake_chat in fake_chats:
        db.session.add(create_chat(fake_chat))
    db.session.commit()

    with open(os.path.join(basedir, "app/populate/fake_posts.json"), "r") as f:
        fake_posts = json.load(f)
    for fake_post in fake_posts:
        db.session.add(create_post(fake_post))
    db.session.commit()


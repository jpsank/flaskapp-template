
from app import db
from app.models.base import Base


class Comment(Base):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(4000))

    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=True)
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)

    votes = db.relationship('CommentVote', backref='comment', lazy='dynamic')

    comments = db.relationship('Comment', lazy='dynamic')

    def score(self):
        return self.votes.filter_by(liked=True).count() - self.votes.filter_by(liked=False).count()


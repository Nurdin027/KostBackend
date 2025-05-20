import uuid
from datetime import datetime

from sqlalchemy.orm import foreign

from _app import db
from _app.models.user import UserModel


class NewsCommentModel(db.Model):
    __tablename__ = "news_comment"

    id = db.Column(db.String(255), primary_key=True, default=lambda: uuid.uuid4().hex)
    news_id = db.Column(db.String(255))
    user_id = db.Column(db.String(255), db.ForeignKey(UserModel.id))
    user = db.relationship(UserModel, foreign_keys=user_id)
    parent_id = db.Column(db.String(255), db.ForeignKey("news_comment.id"))
    child = db.relationship("NewsCommentModel", order_by="NewsCommentModel.add_time")
    comment = db.Column(db.String(255))
    deleted_time = db.Column(db.TIMESTAMP)
    add_time = db.Column(db.TIMESTAMP, default=lambda: datetime.now())

    def __init__(self, news_id, user_id, comment, parent_id=None):
        self.news_id = news_id
        self.user_id = user_id
        self.parent_id = parent_id
        self.comment = comment

    def json(self):
        return {
            "id": self.id,
            "comment": self.comment,
            "user": self.user.full_name if self.user else None,
            "child": [x.json() for x in self.child],
            "add_time": self.add_time.strftime("%d-%m-%Y %H:%M") if self.add_time else None,
        }

    @classmethod
    def by_id(cls, iden):
        return cls.query.filter(cls.id == iden, cls.deleted_time.is_(None)).first()

    @classmethod
    def by_news(cls, news):
        return cls.query.filter(cls.news_id == news, cls.deleted_time.is_(None), cls.parent_id.is_(None)).order_by(cls.add_time.desc()).all()

    @classmethod
    def by_news_user(cls, news, user):
        return cls.query.filter(cls.news_id == news, cls.user_id == user).order_by(cls.add_time.desc()).first()

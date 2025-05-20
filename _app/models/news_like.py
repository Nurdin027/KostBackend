import uuid
from datetime import datetime

from _app import db
from _app.models.user import UserModel


class NewsLikeModel(db.Model):
    __tablename__ = "news_like"

    id = db.Column(db.String(255), primary_key=True, default=lambda: uuid.uuid4().hex)
    news_id = db.Column(db.String(255))
    user_id = db.Column(db.String(255), db.ForeignKey(UserModel.id))
    user = db.relationship(UserModel, foreign_keys=user_id)
    deleted_time = db.Column(db.TIMESTAMP)
    add_time = db.Column(db.TIMESTAMP, default=lambda: datetime.now())

    def __init__(self, news_id, user_id):
        self.news_id = news_id
        self.user_id = user_id

    def json(self):
        return {
            "id": self.id,
            "user": self.user.json() if self.user else None,
            "add_time": self.add_time.strftime("%d-%m-%Y %H:%M") if self.add_time else None,
        }

    @classmethod
    def by_news(cls, news):
        return cls.query.filter(cls.news_id == news, cls.deleted_time.is_(None)).order_by(cls.add_time.desc()).all()

    @classmethod
    def by_news_user(cls, news, user):
        return cls.query.filter(cls.news_id == news, cls.user_id == user).order_by(cls.add_time.desc()).first()

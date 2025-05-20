import uuid
from datetime import datetime

from _app import db


class NewsModel(db.Model):
    __tablename__ = "news"

    id = db.Column(db.String(255), primary_key=True, default=lambda: uuid.uuid4().hex)
    title = db.Column(db.String(255))
    content = db.Column(db.String(255))
    date = db.Column(db.DATE, default=lambda: datetime.now().date())
    is_published = db.Column(db.Integer, default=1)
    add_by = db.Column(db.String(255))
    deleted_time = db.Column(db.TIMESTAMP)
    add_time = db.Column(db.TIMESTAMP, default=lambda: datetime.now())

    def __init__(self, title, content, date, is_published=1):
        self.title = title
        self.content = content
        self.date = date
        self.is_published = is_published

    def json(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "date": self.date.strftime("%d-%m-%Y") if self.date else None,
            "is_published": self.is_published,
            "add_time": self.add_time.strftime("%d-%m-%Y %H:%M") if self.add_time else None,
        }

    @classmethod
    def by_id(cls, iden, lid):
        return cls.query.filter(cls.deleted_time.is_(None), cls.id == iden, cls.id.in_(lid)).first()

    @classmethod
    def get_all(cls, lid):
        return cls.query.filter(cls.deleted_time.is_(None), cls.id.in_(lid)).all()

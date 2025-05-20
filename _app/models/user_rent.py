import uuid
from datetime import datetime

from _app import db


class UserRentModel(db.Model):
    __tablename__ = "user_rent"

    id = db.Column(db.String(255), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = db.Column(db.String(255))
    room_id = db.Column(db.String(255))
    add_time = db.Column(db.TIMESTAMP, default=lambda: datetime.now())

    def __init__(self, user_id, room_id):
        self.user_id = user_id
        self.room_id = room_id

    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "room_id": self.room_id,
            "add_time": self.add_time.strftime("%d-%m-%Y %H:%M") if self.add_time else None,
        }

    @classmethod
    def by_user_room(cls, user, room):
        return cls.query.filter_by(user_id=user, room_id=room).first()

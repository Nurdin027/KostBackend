import uuid
from datetime import datetime

from _app import db


class RoomModel(db.Model):
    __tablename__ = "room"

    id = db.Column(db.String(255), primary_key=True, default=lambda: uuid.uuid4().hex)
    room_name = db.Column(db.String(255))
    number = db.Column(db.Integer)
    building_id = db.Column(db.Integer)
    block_id = db.Column(db.Integer)
    deleted_time = db.Column(db.TIMESTAMP)
    add_time = db.Column(db.TIMESTAMP, default=lambda: datetime.now())

    def __init__(self, room_name, number, block_id):
        self.room_name = room_name
        self.number = number
        self.block_id = block_id

    def json(self):
        return {
            "id": self.id,
            "room_name": self.room_name,
            "number": self.number,
            "building_id": self.building_id,
            "block_id": self.block_id,
            "add_time": self.add_time.strftime("%d-%m-%Y %H:%M") if self.add_time else None,
        }

    @classmethod
    def by_id(cls, iden, lid):
        return cls.query.filter(cls.deleted_time.is_(None), cls.id == iden, cls.id.in_(lid)).first()

    @classmethod
    def get_all(cls, lid):
        return cls.query.filter(cls.deleted_time.is_(None), cls.id.in_(lid)).order_by(cls.number).all()

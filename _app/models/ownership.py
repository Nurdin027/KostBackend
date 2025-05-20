import uuid
from datetime import datetime

from _app import db

import enum


class ListTable(enum.Enum):
    BUILDING = "BUILDING"
    BLOCK = "BLOCK"
    ROOM = "ROOM"
    USER = "USER"
    NEWS = "NEWS"


class OwnershipModel(db.Model):
    __tablename__ = "ownership"

    id = db.Column(db.String(255), primary_key=True, default=lambda: uuid.uuid4().hex)
    admin_id = db.Column(db.String(255))
    table_name = db.Column(db.Enum(ListTable))
    column_id = db.Column(db.String(255))
    add_time = db.Column(db.TIMESTAMP, default=lambda: datetime.now())

    def __init__(self, admin_id, table_name, column_id):
        self.admin_id = admin_id
        self.table_name = table_name
        self.column_id = column_id

    def json(self):
        return {
            "id": self.id,
            "admin_id": self.admin_id,
            "table_name": self.table_name,
            "column_id": self.column_id,
            "add_time": self.add_time.strftime("%d-%m-%Y %H:%M") if self.add_time else None,
        }

    @classmethod
    def find(cls, table_name, column_id, is_list=False):
        q = cls.query.filter(cls.table_name == table_name, column_id == column_id)
        if is_list:
            return q.all()
        return q.first()

    @classmethod
    def get_mine(cls, table_name, admin_id):
        return cls.query.filter(cls.table_name == table_name, cls.admin_id == admin_id).all()

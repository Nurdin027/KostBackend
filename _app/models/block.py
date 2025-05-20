from datetime import datetime

from _app import db


class BlockModel(db.Model):
    __tablename__ = "block"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255))
    building_id = db.Column(db.Integer)
    deleted_time = db.Column(db.TIMESTAMP)
    add_time = db.Column(db.TIMESTAMP, default=lambda: datetime.now())

    def __init__(self, name, building_id):
        self.name = name
        self.building_id = building_id

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "building_id": self.building_id,
            "add_time": self.add_time.strftime("%d-%m-%Y %H:%M") if self.add_time else None,
        }

    @classmethod
    def by_id(cls, iden, lid):
        return cls.query.filter(cls.deleted_time.is_(None), cls.id == iden, cls.id.in_(lid)).first()

    @classmethod
    def get_all(cls, lid):
        return cls.query.filter(cls.deleted_time.is_(None), cls.id.in_(lid)).all()

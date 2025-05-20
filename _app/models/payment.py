import uuid
from datetime import datetime

from _app import db


class PaymentModel(db.Model):
    __tablename__ = "payment"

    id = db.Column(db.String(255), primary_key=True, default=lambda: uuid.uuid4().hex)
    user_id = db.Column(db.String(255))
    rent_id = db.Column(db.String(255))
    date = db.Column(db.DATE, default=lambda: datetime.now().date())
    paid_time = db.Column(db.TIMESTAMP)
    add_time = db.Column(db.TIMESTAMP, default=lambda: datetime.now())

    def __init__(self, user_id, rent_id, date, paid_time=None):
        self.user_id = user_id
        self.rent_id = rent_id
        self.date = date
        self.paid_time = paid_time

    def json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "rent_id": self.rent_id,
            "date": self.date.strftime("%d-%m-%Y") if self.date else None,
            "paid_time": self.paid_time.strftime("%d-%m-%Y %H:%M") if self.paid_time else None,
            "add_time": self.add_time.strftime("%d-%m-%Y %H:%M") if self.add_time else None,
        }

    @classmethod
    def by_rent(cls, rent_id):
        return cls.query.filter(cls.rent_id == rent_id).first()

    @classmethod
    def last_rent(cls, rent_id):
        return cls.query.filter(cls.rent_id == rent_id, cls.paid_time.is_not(None)).order_by(cls.date.desc()).first()

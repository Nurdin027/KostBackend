from datetime import datetime, timedelta

from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from flask_restful import Resource

from _app import db
from _app.global_func import global_parser, responseapi
from _app.models.block import BlockModel
from _app.models.building import BuildingModel
from _app.models.ownership import OwnershipModel
from _app.models.payment import PaymentModel
from _app.models.room import RoomModel
from _app.models.user import UserModel
from os import getenv as cfg

from _app.models.user_rent import UserRentModel


class CreateAdmin(Resource):
    @classmethod
    def post(cls):
        par = global_parser([
            {"name": "key", "type": "str", "req": True},
            {"name": "username", "type": "str", "req": True},
            {"name": "password", "type": "str", "req": True},
        ])
        if par.get("key") == cfg("ADMIN_KEY"):
            try:
                user = UserModel("Admin", par['username'], None, UserModel.encrypt_password(par['password']), auth=1)
                db.session.add(user)
                db.session.commit()
                return responseapi(message="Admin created successfully", data={"username": par['username']})
            except Exception as e:
                print(e)
                return responseapi(500, "error", f"Error: {e}")
        else:
            return responseapi(401, "error", "Invalid Key")


class Login(Resource):
    @classmethod
    def post(cls):
        par = global_parser([
            {"name": "username", "type": "str", "req": True},
            {"name": "password", "type": "str", "req": True},
        ])
        try:
            user = UserModel.get_user(par['username'])
            if user and user.decrypt_password(par['password']):
                access_token = create_access_token(identity=user.id, fresh=True, expires_delta=False)
                refresh_token = create_refresh_token(user.id)
                data = {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user_detail": user.json()
                }
                return responseapi(data=data)
            return responseapi(401, "error", "Incorrect username or password")
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")


class TokenRefresh(Resource):
    @classmethod
    @jwt_required(refresh=True)
    def post(cls):
        try:
            current_user = get_jwt_identity()
            new_token = create_access_token(identity=current_user, fresh=True, expires_delta=False)
            return responseapi(data={"access_token": new_token})
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")


class Rent(Resource):
    @classmethod
    @jwt_required()
    def post(cls):
        par = global_parser([
            {"name": "full_name", "type": "str", "req": True},
            {"name": "username", "type": "str", "req": True},
            {"name": "password", "type": "str", "req": True},
            {"name": "room_id", "type": "str", "req": True},
            {"name": "rent_date", "type": "str", "req": True},
            {"name": "email", "type": "str"},
        ])
        try:
            me = UserModel.by_id(get_jwt_identity())
            if me.auth == 3:
                return responseapi(403, "error", "Access forbidden")
            hash_password = UserModel.encrypt_password(par['password'])
            user = UserModel(par['full_name'], par['username'], par['email'], hash_password)
            db.session.add(user)
            db.session.flush()
            rent = UserRentModel(user.id, par['room_id'])
            db.session.add(rent)
            db.session.flush()
            date = datetime.strptime(par['rent_date'], "%d-%m-%Y")
            payment = PaymentModel(user.id, rent.id, date)
            db.session.add(payment)
            db.session.commit()
            return responseapi(data=user.json())
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")


class UnpaidRent(Resource):
    @classmethod
    @jwt_required()
    def get(cls):
        try:
            me = UserModel.by_id(get_jwt_identity())
            if me.auth == 3:
                return responseapi(403, "error", "Access forbidden")
            elif me.auth == 2:
                ow = OwnershipModel.find("USER", me.id)
                admin_id = ow.id if ow else None
            else:
                admin_id = me.id
            myr = OwnershipModel.get_mine("ROOM", admin_id)
            all_rent = UserRentModel.query.join(PaymentModel, PaymentModel.rent_id == UserRentModel.id, isouter=True) \
                .filter(UserRentModel.room_id.in_([x.column_id for x in myr])).order_by(PaymentModel.date, UserRentModel.add_time).all()
            unpaid = []
            for x in all_rent:
                payment = PaymentModel.query.filter(PaymentModel.rent_id == x.id).order_by(PaymentModel.date.desc()).first()
                if not payment or payment.paid_time is None or (payment.date + timedelta(days=30) < datetime.now().date()):
                    isi = x.json()
                    user = UserModel.by_id(x.user_id)
                    room = RoomModel.by_id(x.room_id, [x.column_id for x in myr])
                    if room:
                        myb = OwnershipModel.get_mine("BLOCK", admin_id)
                        block = BlockModel.by_id(room.block_id, [x.column_id for x in myb])
                    else:
                        block = None
                    if block:
                        myb = OwnershipModel.get_mine("BUILDING", admin_id)
                        building = BuildingModel.by_id(block.building_id, [x.column_id for x in myb])
                    else:
                        building = None
                    if payment:
                        if payment.date + timedelta(days=30) < datetime.now().date():
                            date = (payment.date + timedelta(days=30)).strftime("%d-%m-%Y")
                        else:
                            date = payment.date.strftime("%d-%m-%Y")
                    else:
                        date = None
                    isi.update({
                        "date": date,
                        "user": user.json() if user else None,
                        "room": room.json() if room else None,
                        "block": block.json() if block else None,
                        "building": building.json() if building else None,
                    })
                    unpaid.append(isi)
            return responseapi(data=unpaid)
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")


class PayRent(Resource):
    @classmethod
    @jwt_required()
    def post(cls):
        par = global_parser([
            {"name": "user_id", "type": "str", "req": True},
            {"name": "room_id", "type": "str", "req": True},
        ])
        try:
            me = UserModel.by_id(get_jwt_identity())
            if me.auth == 3:
                return responseapi(403, "error", "Access forbidden")
            rent = UserRentModel.by_user_room(par['user_id'], par['room_id'])
            if not rent:
                return responseapi(404, "error", "Data not found")
            payment = PaymentModel.by_rent(rent.id)
            if not payment:
                last = PaymentModel.last_rent(rent.id)
                date = last.date if last else datetime.now().date()
                payment = PaymentModel(par['user_id'], rent.id, date)
            elif payment.paid_time is None:
                payment.paid_time = datetime.now()
                db.session.commit()
                return responseapi(data=payment.json())
            return responseapi(400, "error", "Rent already paid", data=payment.json())
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")

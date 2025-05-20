from datetime import datetime

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource

from _app import db
from _app.global_func import responseapi, global_parser
from _app.models.block import BlockModel
from _app.models.building import BuildingModel
from _app.models.ownership import OwnershipModel
from _app.models.room import RoomModel
from _app.models.user import UserModel


class Building(Resource):
    @classmethod
    @jwt_required()
    def get(cls):
        me = UserModel.by_id(get_jwt_identity())
        if me.auth > 1:
            ow = OwnershipModel.find("USER", me.id)
            admin_id = ow.id if ow else None
        else:
            admin_id = me.id
        myb = OwnershipModel.get_mine("BUILDING", admin_id)
        return responseapi(data=[x.json() for x in BuildingModel.get_all([x.column_id for x in myb])])

    @classmethod
    @jwt_required()
    def post(cls):
        par = global_parser([
            {"name": "name", "type": "str", "req": True},
            {"name": "address", "type": "str"}
        ])
        try:
            me = UserModel.by_id(get_jwt_identity())
            if me.auth == 3:
                return responseapi(403, "error", "Access forbidden")
            elif me.auth == 2:
                ow = OwnershipModel.find("USER", me.id)
                admin_id = ow.id if ow else None
            else:
                admin_id = me.id
            building = BuildingModel(par['name'], par.get("address"))
            db.session.add(building)
            db.session.flush()
            db.session.add(OwnershipModel(admin_id, "BUILDING", building.id))
            db.session.commit()
            return responseapi(data=building.json())
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")

    @classmethod
    @jwt_required()
    def put(cls, iden):
        par = global_parser([
            {"name": "name", "type": "str"},
            {"name": "address", "type": "str"},
        ])
        try:
            me = UserModel.by_id(get_jwt_identity())
            if me.auth == 3:
                return responseapi(403, "error", "Access forbidden")
            elif me.auth == 2:
                ow = OwnershipModel.find("USER", me.id)
                admin_id = ow.id if ow else None
            else:
                admin_id = me.id
            myb = OwnershipModel.get_mine("BUILDING", admin_id)
            data = BuildingModel.by_id(iden, [x.column_id for x in myb])
            if not data:
                return responseapi(404, "error", "Data not found")
            data.name = par['name']
            data.address = par['address']
            db.session.commit()
            return responseapi(data=data.json())
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")

    @classmethod
    @jwt_required()
    def delete(cls, iden):
        try:
            me = UserModel.by_id(get_jwt_identity())
            if me.auth == 3:
                return responseapi(403, "error", "Access forbidden")
            elif me.auth == 2:
                ow = OwnershipModel.find("USER", me.id)
                admin_id = ow.id if ow else None
            else:
                admin_id = me.id
            myb = OwnershipModel.get_mine("BUILDING", admin_id)
            data = BuildingModel.by_id(iden, [x.column_id for x in myb])
            if not data:
                return responseapi(404, "error", "Data not found")
            data.deleted_time = datetime.now()
            db.session.commit()
            return responseapi()
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")


class Block(Resource):
    @classmethod
    @jwt_required()
    def get(cls):
        me = UserModel.by_id(get_jwt_identity())
        if me.auth > 1:
            ow = OwnershipModel.find("USER", me.id)
            admin_id = ow.id if ow else None
        else:
            admin_id = me.id
        myb = OwnershipModel.get_mine("BLOCK", admin_id)
        return responseapi(data=[x.json() for x in BlockModel.get_all([x.column_id for x in myb])])

    @classmethod
    @jwt_required()
    def post(cls):
        par = global_parser([
            {"name": "name", "type": "str", "req": True},
            {"name": "building_id", "type": "int", "req": True},
        ])
        try:
            me = UserModel.by_id(get_jwt_identity())
            if me.auth == 3:
                return responseapi(403, "error", "Access forbidden")
            elif me.auth == 2:
                ow = OwnershipModel.find("USER", me.id)
                admin_id = ow.id if ow else None
            else:
                admin_id = me.id
            block = BlockModel(par['name'], par['building_id'])
            db.session.add(block)
            db.session.flush()
            db.session.add(OwnershipModel(admin_id, "BLOCK", block.id))
            db.session.commit()
            data = BlockModel.query.all()
            return responseapi(data=[x.json() for x in data])
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")

    @classmethod
    @jwt_required()
    def put(cls, iden):
        par = global_parser([
            {"name": "name", "type": "str", "req": True}
        ])
        try:
            me = UserModel.by_id(get_jwt_identity())
            if me.auth == 3:
                return responseapi(403, "error", "Access forbidden")
            elif me.auth == 2:
                ow = OwnershipModel.find("USER", me.id)
                admin_id = ow.id if ow else None
            else:
                admin_id = me.id
            myb = OwnershipModel.get_mine("BLOCK", admin_id)
            data = BlockModel.by_id(iden, [x.column_id for x in myb])
            if not data:
                return responseapi(404, "error", "Data not found")
            data.name = par['name']
            db.session.commit()
            return responseapi(data=data.json())
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")

    @classmethod
    @jwt_required()
    def delete(cls, iden):
        try:
            me = UserModel.by_id(get_jwt_identity())
            if me.auth == 3:
                return responseapi(403, "error", "Access forbidden")
            elif me.auth == 2:
                ow = OwnershipModel.find("USER", me.id)
                admin_id = ow.id if ow else None
            else:
                admin_id = me.id
            myb = OwnershipModel.get_mine("BLOCK", admin_id)
            data = BlockModel.by_id(iden, [x.column_id for x in myb])
            if not data:
                return responseapi(404, "error", "Data not found")
            data.deleted_time = datetime.now()
            db.session.commit()
            return responseapi()
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")


class Room(Resource):
    @classmethod
    @jwt_required()
    def get(cls):
        me = UserModel.by_id(get_jwt_identity())
        if me.auth > 1:
            ow = OwnershipModel.find("USER", me.id)
            admin_id = ow.id if ow else None
        else:
            admin_id = me.id
        myb = OwnershipModel.get_mine("ROOM", admin_id)
        return responseapi(data=[x.json() for x in RoomModel.get_all([x.column_id for x in myb])])

    @classmethod
    @jwt_required()
    def post(cls):
        par = global_parser([
            {"name": "name", "type": "str", "req": True},
            {"name": "number", "type": "int", "req": True},
            {"name": "block_id", "type": "int", "req": True},
        ])
        try:
            me = UserModel.by_id(get_jwt_identity())
            if me.auth == 3:
                return responseapi(403, "error", "Access forbidden")
            elif me.auth == 2:
                ow = OwnershipModel.find("USER", me.id)
                admin_id = ow.id if ow else None
            else:
                admin_id = me.id
            room = RoomModel(par['name'], par['number'], par['block_id'])
            db.session.add(room)
            db.session.flush()
            db.session.add(OwnershipModel(admin_id, "ROOM", room.id))
            db.session.commit()
            data = RoomModel.query.all()
            return responseapi(data=[x.json() for x in data])
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")

    @classmethod
    @jwt_required()
    def put(cls, iden):
        par = global_parser([
            {"name": "name", "type": "str", "req": True},
            {"name": "number", "type": "int", "req": True},
        ])
        try:
            me = UserModel.by_id(get_jwt_identity())
            if me.auth == 3:
                return responseapi(403, "error", "Access forbidden")
            elif me.auth == 2:
                ow = OwnershipModel.find("USER", me.id)
                admin_id = ow.id if ow else None
            else:
                admin_id = me.id
            myb = OwnershipModel.get_mine("ROOM", admin_id)
            data = RoomModel.by_id(iden, [x.column_id for x in myb])
            if not data:
                return responseapi(404, "error", "Data not found")
            data.room_name = par['name']
            data.number = par['number']
            db.session.commit()
            return responseapi(data=data.json())
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")

    @classmethod
    @jwt_required()
    def delete(cls, iden):
        try:
            me = UserModel.by_id(get_jwt_identity())
            if me.auth == 3:
                return responseapi(403, "error", "Access forbidden")
            elif me.auth == 2:
                ow = OwnershipModel.find("USER", me.id)
                admin_id = ow.id if ow else None
            else:
                admin_id = me.id
            myb = OwnershipModel.get_mine("ROOM", admin_id)
            data = RoomModel.by_id(iden, [x.column_id for x in myb])
            if not data:
                return responseapi(404, "error", "Data not found")
            data.deleted_time = datetime.now()
            db.session.commit()
            return responseapi()
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from os import getenv as cfg

from flask_swagger_ui import get_swaggerui_blueprint

load_dotenv()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = cfg('DB_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = cfg('DEBUG') == 'True'
app.config['SECRET_KEY'] = cfg('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = cfg('JWT_SECRET_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = cfg('JWT_ACCESS_TOKEN_EXPIRES')
app.config['SWAGGER_UI_JSONEDITOR'] = True

db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app)
jwt = JWTManager(app)

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Kost Backend",
        "persistAuthorization": True,
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

from _app.models.block import BlockModel
from _app.models.building import BuildingModel
from _app.models.payment import PaymentModel
from _app.models.room import RoomModel
from _app.models.user_rent import UserRentModel
from _app.models.user import UserModel
from _app.models.ownership import OwnershipModel

# region JWT error
from _app.global_func import responseapi


@jwt.unauthorized_loader
def missing_token_callback(e):
    return responseapi(401, "authorization_required", e)


@jwt.invalid_token_loader
def invalid_token_callback(e):
    return responseapi(401, "invalid_token", e)


# endregion

from _app.resources.assets import Building, Block, Room
from _app.resources.user import Login, CreateAdmin, TokenRefresh, Rent, PayRent, UnpaidRent
from _app.resources.buletin import News, LikeNews, CommentNews

api.add_resource(CreateAdmin, "/api/auth/create-admin")
api.add_resource(Login, "/api/auth/login")
api.add_resource(TokenRefresh, "/api/auth/token/refresh")

api.add_resource(Rent, "/api/rent")
api.add_resource(UnpaidRent, "/api/rent/unpaid")
api.add_resource(PayRent, "/api/rent/pay")

api.add_resource(Building, "/api/assets/building", "/api/assets/building/<iden>")
api.add_resource(Block, "/api/assets/block", "/api/assets/block/<iden>")
api.add_resource(Room, "/api/assets/room", "/api/assets/room/<iden>")

api.add_resource(News, "/api/news", "/api/news/<iden>")
api.add_resource(LikeNews, "/api/news/like/<iden>")
api.add_resource(CommentNews, "/api/news/comment/<iden>")


@app.route('/')
def hello_world():
    return 'Hello World!'

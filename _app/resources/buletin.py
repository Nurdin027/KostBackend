from datetime import datetime
from time import strftime

from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_restful import Resource

from _app import responseapi, db
from _app.global_func import global_parser
from _app.models.news import NewsModel
from _app.models.news_comment import NewsCommentModel
from _app.models.news_like import NewsLikeModel
from _app.models.ownership import OwnershipModel
from _app.models.user import UserModel


class News(Resource):
    @classmethod
    @jwt_required()
    def get(cls):
        me = UserModel.by_id(get_jwt_identity())
        if me.auth > 1:
            ow = OwnershipModel.find("USER", me.id)
            admin_id = ow.id if ow else None
        else:
            admin_id = me.id
        mine = OwnershipModel.get_mine("NEWS", admin_id)
        news = NewsModel.get_all([x.column_id for x in mine])
        data = []
        for x in news:
            isi = x.json()
            likes = NewsLikeModel.by_news(x.id)
            comment = NewsCommentModel.by_news(x.id)
            isi.update({
                "like_count": len(likes or []),
                "likes": [x.json() for x in likes],
                "comment_count": len(comment or []),
                "comments": [x.json() for x in comment],
            })
            data.append(isi)
        return responseapi(data=data)

    @classmethod
    @jwt_required()
    def post(cls):
        par = global_parser([
            {"name": "title", "type": "str", "req": True},
            {"name": "content", "type": "str", "req": True},
            {"name": "date", "type": "str"}
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
            date = datetime.strptime(par['date'], "%d-%m-%Y") if par.get("date") else datetime.now().date()
            news = NewsModel(par['title'], par['content'], date)
            db.session.add(news)
            db.session.flush()
            db.session.add(OwnershipModel(admin_id, "NEWS", news.id))
            db.session.commit()
            return responseapi(data=news.json())
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")

    @classmethod
    @jwt_required()
    def put(cls, iden):
        par = global_parser([
            {"name": "title", "type": "str"},
            {"name": "content", "type": "str"},
            {"name": "date", "type": "str"},
            {"name": "is_published", "type": "int"}
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
            myb = OwnershipModel.get_mine("NEWS", admin_id)
            data = NewsModel.by_id(iden, [x.column_id for x in myb])
            if not data:
                return responseapi(404, "error", "Data not found")
            data.title = par.get('title') or data.title
            data.content = par.get('content') or data.content
            data.date = datetime.strptime(par['date'], "%d-%m-%Y") if par.get('date') else data.date
            data.is_published = par.get('is_published') or data.is_published
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
            myb = OwnershipModel.get_mine("NEWS", admin_id)
            data = NewsModel.by_id(iden, [x.column_id for x in myb])
            if not data:
                return responseapi(404, "error", "Data not found")
            data.deleted_time = datetime.now()
            db.session.commit()
            return responseapi()
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")


class LikeNews(Resource):
    @classmethod
    @jwt_required()
    def post(cls, iden):
        try:
            me = UserModel.by_id(get_jwt_identity())
            if me.auth > 1:
                ow = OwnershipModel.find("USER", me.id)
                admin_id = ow.id if ow else None
            else:
                admin_id = me.id
            myb = OwnershipModel.get_mine("NEWS", admin_id)
            news = NewsModel.by_id(iden, [x.column_id for x in myb])
            if not news:
                return responseapi(404, "error", "Data not found")
            ada = NewsLikeModel.by_news_user(news.id, me.id)
            if ada:
                ada.deleted_time = None if ada.deleted_time else datetime.now()
            else:
                db.session.add(NewsLikeModel(news.id, me.id))
            db.session.commit()
            data = news.json()
            likes = NewsLikeModel.by_news(news.id)
            data.update({
                "like_count": len(likes or []),
                "likes": [x.json() for x in likes],
            })
            return responseapi(data=data)
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")


class CommentNews(Resource):
    @classmethod
    @jwt_required()
    def post(cls, iden):
        try:
            par = global_parser([
                {"name": "comment", "type": "str", "req": True},
                {"name": "parent_id", "type": "str"},
            ])
            me = UserModel.by_id(get_jwt_identity())
            if me.auth > 1:
                ow = OwnershipModel.find("USER", me.id)
                admin_id = ow.id if ow else None
            else:
                admin_id = me.id
            myb = OwnershipModel.get_mine("NEWS", admin_id)
            news = NewsModel.by_id(iden, [x.column_id for x in myb])
            if not news:
                return responseapi(404, "error", "Data not found")
            db.session.add(NewsCommentModel(iden, me.id, par['comment'], par.get('parent_id')))
            db.session.commit()
            data = news.json()
            comment = NewsCommentModel.by_news(news.id)
            data.update({
                "comment_count": len(comment or []),
                "comment": [x.json() for x in comment],
            })
            return responseapi(data=data)

        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")

    @classmethod
    @jwt_required()
    def put(cls, iden):
        try:
            par = global_parser([
                {"name": "comment", "type": "str"},
            ])
            comment = NewsCommentModel.by_id(iden)
            if not comment:
                return responseapi(404, "error", "Data not found")
            comment.comment = par['comment']
            db.session.commit()
            return responseapi(data=comment.json())

        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")

    @classmethod
    @jwt_required()
    def delete(cls, iden):
        try:
            comment = NewsCommentModel.by_id(iden)
            if not comment:
                return responseapi(404, "error", "Data not found")
            # comment.deleted_time = datetime.now()
            db.session.delete(comment)
            db.session.commit()
            return responseapi()
        except Exception as e:
            print(e)
            return responseapi(500, "error", f"Error: {e}")

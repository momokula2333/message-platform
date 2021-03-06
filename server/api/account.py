from flask import request, jsonify, Blueprint
from flask_jwt_extended import JWTManager, jwt_required,\
    create_access_token, get_jwt_identity, fresh_jwt_required, jwt_refresh_token_required

from pony.orm import db_session, exists, commit
from pony.orm.serialization import json_converter
from server.model import User
import datetime

account = Blueprint('account', __name__)


@account.route('/register', methods=['post'])
@db_session
def register():
    req = request.get_json()
    if not exists(u.id for u in User if u.username == req['display_name']):
        now = datetime.datetime.now()
        User(username=req['display_name'],
             gender=req['gender'],
             avatar=req['avatar'],
             age=req['age'],
             user_id=now,
             password=req['password'],
             created_at=now)
        user = User.get(username=req['display_name'])
        return jsonify(success=True, user=user.describe(), access_token=create_access_token(identity=user.describe()))
    else:
        return jsonify(success=False, err='INVAILD_USERNAME')


@account.route('/login', methods=['POST'])
@db_session
def login():
    req = request.get_json(force=True)
    user = User.get(username=req['display_name'])
    if not user:
        return jsonify(success=False,err="INVAILD_USER")
    if user.password == req['password']:
        return jsonify(success=True, user=user.describe(), access_token=create_access_token(identity=user.id))
    else:
        return jsonify(success=False, err="INVAILD_PASSWORD")

@account.route('/myprofile')
@db_session
@jwt_required
def protected():
    current_id = get_jwt_identity()
    user = User.get(id=current_id)
    if not user:
        return jsonify(err='INVALID_AUTHORIZATION'), 401
    return jsonify(user=user.describe()), 200

@account.route('/refresh')
@db_session
@fresh_jwt_required
def refresh():
    current_id = get_jwt_identity()
    user = User.get(id=current_id)
    if not user:
        return jsonify(err='INVALID_AUTHORIZATION'), 401
    return jsonify(user=user.describe()), 200

# @account.route('/protected')
# @db_session
# @fresh_jwt_required
# def protected():
#     current_id = get_jwt_identity()
#     user = User.get(id=current_id)
#     if not user:
#         return jsonify(err='INVALID_AUTHORIZATION'), 401
#     return jsonify(user=user.describe()), 200

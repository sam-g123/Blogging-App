from flask import jsonify, request, url_for, g
from . import api
from .. import db
from ..models import User
from .errors import bad_request

@api.route('/users/', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_json() for user in users])

@api.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())

@api.route('/users/', methods=['POST'])
def create_user():
    user_data = request.get_json()
    if not user_data:
        return bad_request('You must post JSON data.')
    user = User.from_json(user_data)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_json()), 201, {'Location': url_for('api.get_user', id=user.id)}

from flask import jsonify, request, url_for, g
from . import api
from .. import db
from ..models import Comment
from .errors import bad_request

@api.route('/comments/', methods=['GET'])
def get_comments():
    comments = Comment.query.all()
    return jsonify([comment.to_json() for comment in comments])

@api.route('/comments/<int:id>', methods=['GET'])
def get_comment(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())

@api.route('/comments/', methods=['POST'])
def create_comment():
    comment_data = request.get_json()
    if not comment_data:
        return bad_request('You must post JSON data.')
    comment = Comment.from_json(comment_data)
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json()), 201, {'Location': url_for('api.get_comment', id=comment.id)}

from flask_httpauth import HTTPBasicAuth
from .errors import unauthorized, forbidden
from ..models import User
from .import api
from flask import g, jsonify
from ..exceptions import ValidationError

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        return False
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)

@api.route('/tokens/', methods=['POST'])
@auth.login_required
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(expiration=3600), 'expiration': 3600})


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')

# Check authentication automatically for all the routes in the blueprint
# Reject authenticated users who have not confirmed their accounts.
@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('Unconfirmed account')

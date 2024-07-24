# app/auth.py
import os
from flask import session, redirect, url_for, request
from google_auth_oauthlib.flow import Flow
import google.oauth2.credentials
from . import auth

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1' # This line should be removed if using HTTPS

@auth.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(
        os.getenv('CLIENT_SECRETS_FILE'),
        scopes=['https://www.googleapis.com/auth/gmail.send'],
        redirect_uri=url_for('auth.oauth2callback', _external=True)
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    session['state'] = state
    return redirect(authorization_url)

@auth.route('/oauth2callback')
def oauth2callback():
    state = session.get('state', None)
    if state is None or state != request.args.get('state'):
        return "Invalid state parameter", 401

    flow = Flow.from_client_secrets_file(
        os.getenv('CLIENT_SECRETS_FILE'),
        scopes=['https://www.googleapis.com/auth/gmail.send'],
        state=state,
        redirect_uri=url_for('auth.oauth2callback', _external=True)
    )

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('auth.register'))

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

# app/emails.py

import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from flask import current_app, session, render_template
from google.oauth2.credentials import Credentials
import google.auth.transport.requests


def get_credentials():
    credentials_info = session.get('credentials')
    if not credentials_info:
        raise Exception("No OAuth2 credentials available")

    credentials = Credentials(
        credentials_info['token'],
        refresh_token=credentials_info['refresh_token'],
        token_uri=credentials_info['token_uri'],
        client_id=credentials_info['client_id'],
        client_secret=credentials_info['client_secret'],
        scopes=credentials_info['scopes']
    )

    if credentials.expired:
        request = google.auth.transport.requests.Request()
        credentials.refresh(request)
        session['credentials'] = credentials_to_dict(credentials)

    return credentials


def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }


def send_email(to, subject, template, **kwargs):
    credentials = get_credentials()
    service = build('gmail', 'v1', credentials=credentials)

    app = current_app._get_current_object()
    body = render_template(template + '.txt', **kwargs)
    html_body = render_template(template + '.html', **kwargs)
    
    message = MIMEText(body, 'plain')
    message['to'] = to
    message['subject'] = app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message = {'raw': raw_message}

    try:
        service.users().messages().send(userId='me', body=message).execute()
    except Exception as e:
        current_app.logger.error(f'Error sending email: {e}')
        raise

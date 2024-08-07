import unittest
from unittest.mock import patch, MagicMock
import re
from app import create_app, db
from app.models import Role, User
from app.emails import get_credentials

class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)
        db.create_all()
        Role.insert_roles()
        user = User(email='user@example.com', username='john', password='password', confirmed=True)
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Posts', response.get_data(as_text=True))

@patch('app.emails.get_credentials')
def test_register(self, MockGetCredentials):
    mock_credentials = MagicMock()
    mock_credentials.universe_domain = 'googleapis.com'
    mock_credentials.create_scoped.side_effect = lambda scopes: mock_credentials
    mock_credentials.authorize.side_effect = lambda: mock_credentials
    MockGetCredentials.return_value = mock_credentials
    response = self.client.post('/register', data={
        'email': 'newuser@example.com',
        'username': 'newuser',
        'password': 'password',
        'password2': 'password'
    })
    self.assertEqual(response.status_code, 302)
    user = User.query.filter_by(email='newuser@example.com').first()
    self.assertIsNotNone(user)

@patch('app.emails.get_credentials') 
def test_account_confirmation(self, MockGetCredentials):
    mock_credentials = MagicMock()
    mock_credentials.universe_domain = 'googleapis.com'
    mock_credentials.create_scoped.side_effect = lambda scopes: mock_credentials
    mock_credentials.authorize.side_effect = lambda: mock_credentials
    MockGetCredentials.return_value = mock_credentials

    response = self.client.post('/register', data={
        'email': 'newuser@example.com',
        'username': 'newuser',
        'password': 'password',
        'password2': 'password'
    })
    self.assertEqual(response.status_code, 302)

    user = User.query.filter_by(email='newuser@example.com').first()
    self.assertIsNotNone(user)

    token = user.generate_confirmation_token()

    response = self.client.get(f'/confirm/{token}', follow_redirects=True)
    self.assertEqual(response.status_code, 200)
    self.assertIn('You have confirmed your account', response.get_data(as_text=True))
    self.assertTrue(user.confirmed)

    @patch('app.emails.get_credentials')
    def test_login(self, MockGetCredentials):
        mock_credentials = MagicMock()
        mock_credentials.universe_domain = 'googleapis.com'

        mock_credentials.create_scoped.side_effect = lambda scopes: mock_credentials
        mock_credentials.authorize.side_effect = lambda: mock_credentials

        MockGetCredentials.return_value = mock_credentials

        response = self.client.post('/login', data={
            'email': 'user@example.com',
            'password': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(re.search('Hello, john!', response.get_data(as_text=True)))

    @patch('app.emails.get_credentials')
    def test_logout(self, MockGetCredentials):
        mock_credentials = MagicMock()
        mock_credentials.universe_domain = 'googleapis.com'

        mock_credentials.create_scoped.side_effect = lambda scopes: mock_credentials
        mock_credentials.authorize.side_effect = lambda: mock_credentials

        MockGetCredentials.return_value = mock_credentials

        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Please log in to access this page', response.get_data(as_text=True))

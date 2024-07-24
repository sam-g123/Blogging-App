# tests/test_api.py
import unittest
from flask import url_for
from app import create_app, db
from app.models import Role, User, Post
from faker import Faker

fake = Faker()

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()

        db.create_all()
        Role.insert_roles()
        self.generate_fake_data()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def generate_fake_data(self):
        user = User(email='user@example.com', username='john', password='password', confirmed=True)
        db.session.add(user)
        db.session.commit()

        post = Post(body='Test post', author=user)
        db.session.add(post)
        db.session.commit()

    def test_no_auth(self):
        response = self.client.get(url_for('api.get_posts'),
                                    content_type='application/json')
        self.assertEqual(response.status_code, 401)

    def test_posts(self):
        self.client.post(url_for('auth.login'), data={
            'email': 'user@example.com',
            'password': 'password'
        })
        response = self.client.get(url_for('api.get_posts'))
        self.assertEqual(response.status_code, 200)


        # ...
    def get_api_headers(self, username, password):
        return {
            'Authorization':
                'Basic ' + b64encode(
                    (username + ':' + password).encode('utf-8')).decode('utf-8'),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

        # write a post
        response = self.client.post(
            '/api/v1/posts/',
            headers=self.get_api_headers('user@example.com', 'password'),
            data=json.dumps({'body': 'body of the *blog* post'}))
        self.assertEqual(response.status_code, 201)
        url = response.headers.get('Location')
        self.assertIsNotNone(url)
 
        # get the new post
        response = self.client.get(
            url,
            headers=self.get_api_headers('user@example.com', 'password'))
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual('http://localhost' + json_response['url'], url)
        self.assertEqual(json_response['body'], 'body of the *blog* post')
        self.assertEqual(json_response['body_html'],
                        '<p>body of the <em>blog</em> post</p>')



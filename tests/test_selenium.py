# tests/test_selenium.py
import unittest
import re
import threading
import random
from selenium import webdriver
from app import create_app, db
from app.models import Role, User, Post
from faker import Faker
import time

fake = Faker()

class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        try:
            cls.client = webdriver.Chrome(options=options)
        except:
            pass

        if cls.client:
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel("ERROR")
            
            db.create_all()
            Role.insert_roles()
            cls.generate_fake_data(10, 10)

            admin_role = Role.query.filter_by(permissions=0xff).first()
            admin = User(email='user@example.com', username='john', password='password', role=admin_role, confirmed=True)
            db.session.add(admin)
            db.session.commit()

            cls.server_thread = threading.Thread(
                target=cls.app.run, kwargs={'debug': 'false', 'use_reloader': False, 'use_debugger': False}
            )
            cls.server_thread.start()
            time.sleep(2)  # Wait for the server to start

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            cls.client.get('http://127.0.0.1:5000/shutdown')
            cls.client.quit()
            cls.server_thread.join()

            db.drop_all()
            db.session.remove()

            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

    def test_admin_home_page(self):
        self.client.get('http://localhost:5000/')
        self.assertTrue(re.search('Hello,\s+Stranger!', self.client.page_source))

        self.client.find_element_by_link_text('Log In').click()
        self.assertIn('<h1>Login</h1>', self.client.page_source)

        self.client.find_element_by_name('email').send_keys('user@example.com')
        self.client.find_element_by_name('password').send_keys('password')
        self.client.find_element_by_name('submit').click()
        self.assertTrue(re.search('Hello,\s+john!', self.client.page_source))

        self.client.find_element_by_link_text('Profile').click()
        self.assertIn('<h1>john</h1>', self.client.page_source)

    @classmethod
    def generate_fake_data(cls, user_count, post_count):
        users = []
        for _ in range(user_count):
            user = User(email=fake.email(), username=fake.user_name(), password='password', confirmed=True)
            db.session.add(user)
            users.append(user)
        db.session.commit()

        for _ in range(post_count):
            user = random.choice(users)
            post = Post(body=fake.text(max_nb_chars=200), timestamp=fake.past_date(), author=user)
            db.session.add(post)
        db.session.commit()

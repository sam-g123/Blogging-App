import unittest
from app import create_app, db
from app.models import User, Role, Permission, AnonymousUser, Post, Comment
from werkzeug.security import generate_password_hash
from datetime import datetime

class ModelTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app('testing')
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

        Role.insert_roles()

        admin_role = Role.query.filter_by(permissions=0xff).first()
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(email='admin@example.com', username='admin', password='password', role=admin_role, confirmed=True)
            db.session.add(admin)
            db.session.commit()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        db.session.remove()
        db.drop_all()
        db.create_all()

    def test_password_setter(self):
        u = User(email='passwordsetter@example.com', username='passwordsetter', password='password')
        self.assertIsNotNone(u.password_hash)

    def test_no_password_getter(self):
        u = User(email='nopasswordgetter@example.com', username='nopasswordgetter', password='password')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(email='passwordverification@example.com', username='passwordverification', password='password')
        self.assertTrue(u.verify_password('password'))
        self.assertFalse(u.verify_password('dog'))

    def test_password_salts_are_random(self):
        u = User(email='passwordsalt1@example.com', username='passwordsalt1', password='password')
        u2 = User(email='passwordsalt2@example.com', username='passwordsalt2', password='password')
        self.assertNotEqual(u.password_hash, u2.password_hash)

    def test_user_role(self):
        role = Role.query.filter_by(name='User').first()
        if not role:
            role = Role(name='User', permissions=Permission.FOLLOW)
            db.session.add(role)
            db.session.commit()
        
        u = User(email='userrole@example.com', username='userrole', password='password', role=role)
        db.session.add(u)
        db.session.commit()

        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.MODERATE))

    def test_anonymous_user(self):
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_user_string_representation(self):
        u = User(email='stringrepresentation@example.com', username='stringrepresentation', password='password')
        db.session.add(u)
        db.session.commit()
        self.assertEqual(str(u), '<User stringrepresentation>')

    def test_user_token_generation(self):
        u = User(email='token@example.com', username='token', password='password')
        db.session.add(u)
        db.session.commit()
        token = u.generate_auth_token()
        self.assertTrue(u.verify_auth_token(token))

    def test_user_post_relationship(self):
        u = User(email='postrelationship@example.com', username='postrelationship', password='password')
        db.session.add(u)
        db.session.commit()
        post = Post(body='test post', author=u)
        db.session.add(post)
        db.session.commit()
        self.assertIn(post, u.posts)

    def test_role_creation(self):
        role = Role(name='TestRole')
        db.session.add(role)
        db.session.commit()
        self.assertIsNotNone(role.id)
        self.assertEqual(role.name, 'TestRole')

    def test_role_permissions(self):
        role = Role(name='TestRole')
        role.add_permission(Permission.FOLLOW)
        role.add_permission(Permission.COMMENT)
        self.assertTrue(role.has_permission(Permission.FOLLOW))
        self.assertTrue(role.has_permission(Permission.COMMENT))
        self.assertFalse(role.has_permission(Permission.WRITE))
        role.remove_permission(Permission.FOLLOW)
        self.assertFalse(role.has_permission(Permission.FOLLOW))
        role.reset_permissions()
        self.assertFalse(role.has_permission(Permission.COMMENT))

    def test_follow_relationship(self):
        u1 = User(email='user1@example.com', username='user1', password='password')
        u2 = User(email='user2@example.com', username='user2', password='password')
        db.session.add_all([u1, u2])
        db.session.commit()
        u1.follow(u2)
        db.session.commit()
        self.assertTrue(u1.is_following(u2))
        self.assertFalse(u2.is_following(u1))
        self.assertTrue(u2.is_followed_by(u1))
        u1.unfollow(u2)
        db.session.commit()
        self.assertFalse(u1.is_following(u2))

    def test_post_creation(self):
        u = User(email='post@example.com', username='post', password='password')
        db.session.add(u)
        db.session.commit()
        post = Post(body='test post', author=u)
        db.session.add(post)
        db.session.commit()
        self.assertIsNotNone(post.id)
        self.assertEqual(post.body, 'test post')
        self.assertEqual(post.author, u)

    def test_post_body_html(self):
        post = Post(body='This is a *test* post with [link](http://example.com).')
        db.session.add(post)
        db.session.commit()
        self.assertIsNotNone(post.body_html)
        self.assertIn('<em>test</em>', post.body_html)
        self.assertIn('<a href="http://example.com"', post.body_html)

    def test_comment_creation(self):
        u = User(email='comment@example.com', username='comment', password='password')
        p = Post(body='test post')
        db.session.add_all([u, p])
        db.session.commit()
        comment = Comment(body='test comment', author=u, post=p)
        db.session.add(comment)
        db.session.commit()
        self.assertIsNotNone(comment.id)
        self.assertEqual(comment.body, 'test comment')
        self.assertEqual(comment.author, u)
        self.assertEqual(comment.post, p)

    def test_user_creation(self):
        u = User(email='newuser@example.com', username='newuser', password='password')
        db.session.add(u)
        db.session.commit()
        self.assertIsNotNone(u.id)
        self.assertEqual(u.email, 'newuser@example.com')
        self.assertEqual(u.username, 'newuser')
        self.assertTrue(u.verify_password('password'))

    def test_user_follow_posts(self):
        u1 = User(email='user1@example.com', username='user1', password='password')
        u2 = User(email='user2@example.com', username='user2', password='password')
        db.session.add_all([u1, u2])
        db.session.commit()
        p1 = Post(body='post from user1', author=u1)
        p2 = Post(body='post from user2', author=u2)
        db.session.add_all([p1, p2])
        u1.follow(u2)
        db.session.commit()
        followed_posts = u1.followed_posts.all()
        self.assertIn(p2, followed_posts)
        self.assertIn(p1, followed_posts)  # user's own posts are included

    def test_user_confirm(self):
        u = User(email='confirm@example.com', username='confirm', password='password')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))
        self.assertTrue(u.confirmed)

    def test_user_ping(self):
        u = User(email='ping@example.com', username='ping', password='password')
        db.session.add(u)
        db.session.commit()
        last_seen_before = u.last_seen
        u.ping()
        db.session.refresh(u)
        self.assertTrue(u.last_seen > last_seen_before)
    
def test_to_json(self):
    u = User(email='json@example.com', username='json', password='password')
    db.session.add(u)
    db.session.commit()
    with self.app.test_request_context('/'):
        json_user = u.to_json()
        self.assertEqual(json_user['username'], 'json')
        self.assertIn('url', json_user)
        self.assertIn('posts_url', json_user)
        self.assertEqual(json_user['url'], url_for('api.get_user', id=u.id, _external=True))
        self.assertEqual(json_user['posts_url'], url_for('api.get_posts', _external=True))
        self.assertNotIn('followed_posts_url', json_user)
        self.assertEqual(json_user['post_count'], u.posts.count())

if __name__ == '__main__':
    unittest.main()

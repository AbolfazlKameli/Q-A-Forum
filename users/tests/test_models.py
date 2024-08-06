from django.test import TestCase
from model_bakery import baker

from users.models import User


class TestUser(TestCase):
    def setUp(self):
        self.user = baker.make(User, username='username', email='email@gmail.com', is_active=True)
        self.not_active_user = baker.make(User, username='not_active', email='not_active@gmail.com')
        self.admin_user = baker.make(User, username='admin', email='admin@gmail.com', is_admin=True, is_active=True)

    def test_user_str(self):
        self.assertEqual(str(self.user), 'username - email@gmail.com')
        self.assertEqual(str(self.admin_user), 'admin - admin@gmail.com')
        self.assertEqual(str(self.not_active_user), 'not_active - not_active@gmail.com')

    def test_username_field(self):
        self.assertEqual(self.user.USERNAME_FIELD, 'email')

    def test_user_active(self):
        self.assertTrue(self.user.is_active)

    def test_user_not_active(self):
        self.assertFalse(self.not_active_user.is_active)

    def test_user_is_admin(self):
        self.assertTrue(self.admin_user.is_admin)
        self.assertTrue(self.admin_user.is_staff)

    def test_user_is_not_admin(self):
        self.assertFalse(self.user.is_admin)
        self.assertFalse(self.user.is_staff)

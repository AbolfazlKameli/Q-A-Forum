from model_bakery import baker
from rest_framework.test import APITestCase

from users.models import User
from users.serializers import (
    UserSerializer,
    UserRegisterSerializer,
    ResendVerificationEmailSerializer,
    ChangePasswordSerializer,
    SetPasswordSerializer
)


class TestUserSerializer(APITestCase):
    @classmethod
    def setUpTestData(cls):
        baker.make(User, username='username', email='email@gmail.com', is_active=True)

    def test_valid_data(self):
        data = {'username': 'kevin', 'email': 'kevin@gmail.com', 'password': 'password', 'is_active': True}
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['username'], 'kevin')

    def test_empty_fields(self):
        serializer = UserSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 2)

    def test_invalid_username(self):
        data = {'username': 'username', 'email': 'another_email@gmail.com', 'password': 'password'}
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 1)
        self.assertEqual(serializer.errors['username'][0], 'user with this username already exists.')

    def test_invalid_email(self):
        data = {'username': 'another_username', 'email': 'email@gmail.com', 'password': 'password'}
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 1)
        self.assertEqual(serializer.errors['email'][0], 'user with this email already exists.')


class TestUserRegisterSerializer(APITestCase):
    @classmethod
    def setUpTestData(cls):
        baker.make(User, username='username', email='email@gmail.com', is_active=True)

    def test_valid_data(self):
        data = {'username': 'kevin', 'email': 'kevin@gmail.com', 'password': 'asdF@123', 'password2': 'asdF@123'}
        serializer = UserRegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['username'], 'kevin')

    def test_common_password(self):
        data = {'username': 'kevin', 'email': 'kevin@gmail.com', 'password': 'password', 'password2': 'password'}
        serializer = UserRegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 1)
        self.assertEqual(serializer.errors['non_field_errors'][0], 'This password is too common.')

    def test_passwords_dont_match(self):
        data = {'username': 'kevin', 'email': 'kevin@gmail.com', 'password': 'password', 'password2': 'not_matched'}
        serializer = UserRegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 1)
        self.assertEqual(serializer.errors['non_field_errors'][0], 'Passwords must match.')

    def test_not_unique_username(self):
        data = {'username': 'username', 'email': 'kevin@gmail.com', 'password': 'asdF@123', 'password2': 'asdF@123'}
        serializer = UserRegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 1)
        self.assertEqual(serializer.errors['username'][0], 'user with this username already exists.')

    def test_not_unique_email(self):
        data = {'username': 'kevin', 'email': 'email@gmail.com', 'password': 'asdF@123', 'password2': 'asdF@123'}
        serializer = UserRegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 1)
        self.assertEqual(serializer.errors['email'][0], 'user with this email already exists.')

    def test_empty_password2(self):
        data = {'username': 'kevin', 'email': 'kevin@gmail.com', 'password': 'asdF@123'}
        serializer = UserRegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 1)
        self.assertEqual(serializer.errors['password2'][0], 'This field is required.')

    def test_empty_fields(self):
        serializer = UserRegisterSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 4)


class TestResendVerificationEmailSerializer(APITestCase):
    @classmethod
    def setUpTestData(cls):
        baker.make(User, username='username', email='email@gmail.com')

    def test_valid_data(self):
        serializer = ResendVerificationEmailSerializer(data={'email': 'email@gmail.com'})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(str(serializer.validated_data['user']), 'username - email@gmail.com')

    def test_invalid_email(self):
        serializer = ResendVerificationEmailSerializer(data={'email': 'kevin@gmail.com'})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 1)
        self.assertEqual(serializer.errors['non_field_errors'][0], 'User does not exist!')

    def test_pre_active_user(self):
        baker.make(User, username='PreActiveUser', email='active@gmail.com', is_active=True)
        serializer = ResendVerificationEmailSerializer(data={'email': 'active@gmail.com'})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 1)
        self.assertEqual(serializer.errors['non_field_errors'][0], 'Account already active!')


class TestChangePasswordSerializer(APITestCase):
    def setUp(self):
        self.user = baker.make(User, is_active=True, password='password')

    def test_valid_data(self):
        data = {'old_password': 'password', 'new_password': 'root13245', 'confirm_new_password': 'root13245'}
        serializer = ChangePasswordSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_common_password(self):
        data = {'old_password': 'password', 'new_password': 'password', 'confirm_new_password': 'password'}
        serializer = ChangePasswordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 1)
        self.assertEqual(serializer.errors['non_field_errors'][0], 'This password is too common.')

    def test_passwords_dont_match(self):
        data = {'old_password': 'password', 'new_password': 'root13245', 'confirm_new_password': 'password'}
        serializer = ChangePasswordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 1)
        self.assertEqual(serializer.errors['non_field_errors'][0], 'Passwords must match')

    def test_missing_fields(self):
        data = {'new_password': 'root13245'}
        serializer = ChangePasswordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 2)

    def test_empty_fields(self):
        serializer = ChangePasswordSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 3)


class TestSetPasswordSerializer(APITestCase):
    def test_valid_data(self):
        data = {'new_password': 'root13245', 'confirm_new_password': 'root13245'}
        serializer = SetPasswordSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_common_password(self):
        data = {'new_password': 'password', 'confirm_new_password': 'password'}
        serializer = SetPasswordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 1)
        self.assertEqual(serializer.errors['non_field_errors'][0], 'This password is too common.')

    def test_passwords_dont_match(self):
        data = {'new_password': 'root13245', 'confirm_new_password': 'password'}
        serializer = SetPasswordSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(len(serializer.errors), 1)
        self.assertEqual(serializer.errors['non_field_errors'][0], 'Passwords must match')

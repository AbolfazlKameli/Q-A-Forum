from datetime import datetime
from unittest.mock import patch
from urllib.parse import urlencode

import jwt
from model_bakery import baker
from rest_framework.test import APIRequestFactory, APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from users.views import *


class TestUsersListAPI(APITestCase):
    @classmethod
    def setUpTestData(cls):
        baker.make(User, 34)

    def setUp(self):
        self.factory = APIRequestFactory()
        self.user = baker.make(User, username='username', email='email@gmail.com', password='password', is_active=True)
        self.not_active_user = baker.make(User, username='not_active', email='not_active@gmail.com',
                                          password='password')
        self.user_token = str(AccessToken.for_user(self.user))
        self.admin = baker.make(User, username='admin', email='admin@gmail.com', password='admin', is_active=True,
                                is_admin=True)
        self.admin_token = str(AccessToken.for_user(self.admin))

    def test_permission_denied(self):
        request = self.factory.get(reverse('users:users_list'), HTTP_AUTHORIZATION='Bearer ' + self.user_token)
        response = UsersListAPI.as_view()(request)
        self.assertEqual(response.status_code, 403)

    def test_list_GET(self):
        request = self.factory.get(reverse('users:users_list'), HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = UsersListAPI.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 20)

    def test_list_paginated_GET(self):
        request = self.factory.get(f"{reverse('users:users_list')}?{urlencode({'page': 2})}",
                                   HTTP_AUTHORIZATION='Bearer ' + self.admin_token)
        response = UsersListAPI.as_view()(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 17)


class TestUserRegisterAPI(APITestCase):
    @classmethod
    def setUpTestData(cls):
        baker.make(User, is_active=True, username='username', email='email')

    def setUp(self):
        self.url = reverse('users:user_register')
        self.valid_data = {
            'username': 'kevin',
            'email': 'kevin@example.com',
            'password': 'asdF@123',
            'password2': 'asdF@123',
        }
        self.invalid_data = {
            'username': 'username',
            'email': 'amir@example.com',
            'password': 'asdF@123',
            'password2': 'asdF@123',
        }

    def test_success_register(self):
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)
        self.assertIn('data', response.data)
        self.assertEqual(User.objects.all().count(), 2)

    def test_not_unique_username(self):
        response = self.client.post(self.url, data=self.invalid_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
        self.assertIn('username', response.data['error'])

    def test_mismatch_password(self):
        self.invalid_data['password'] = '<PASSWORD>'
        self.invalid_data['username'] = 'testuser'
        response = self.client.post(self.url, data=self.invalid_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)

    def test_register_with_avatar(self):
        self.valid_data['avatar'] = 'avatar.png'
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, 200)


class TestUserRegisterVerificationAPI(APITestCase):
    def setUp(self):
        self.url = reverse('users:user_register_verify', args=['invalid_token'])
        self.user = baker.make(User, is_active=False)
        self.token = JWT_token.generate_token(self.user)

    def create_expired_token(self):
        payload = {
            'user_id': self.user.id,
            'exp': datetime.now() - timedelta(days=34)
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

    def test_account_activation_success(self):
        response = self.client.get(self.url.replace('invalid_token', self.token['token']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Account activated successfully')
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_account_already_active(self):
        self.user.is_active = True
        self.user.save()
        response = self.client.get(self.url.replace('invalid_token', self.token['token']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'this account already is active')

    @patch('users.views.get_object_or_404')
    def test_activation_url_invalid(self, mock_jwt_decode_token):
        mock_jwt_decode_token.side_effect = Http404
        response = self.client.get(self.url.replace('invalid_token', self.token['token']))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Activation URL is invalid')

    def test_invalid_token(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Activation link is invalid!')

    def test_expired_token(self):
        expired_token = self.create_expired_token()
        response = self.client.get(self.url.replace('invalid_token', expired_token))
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Activation link has expired!')


class TestResendVerificationEmailAPI(APITestCase):
    def setUp(self):
        self.url = reverse('users:user_register_resend_email')
        self.user = baker.make(User, is_active=False, email='email@gmail.com')
        self.active_user = baker.make(User, is_active=True, email='active_user@gmail.com')

    def test_successful_send_email(self):
        data = {'email': 'email@gmail.com'}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'The activation email has been sent again successfully')

    @patch('utils.send_email.send_link')
    def test_invalid_email(self, mock_send_email):
        data = {'email': 'does_not_exists_user_email@gmail.com'}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('errors', response.data)
        self.assertEqual(response.data['errors']['non_field_errors'][0], 'User does not exist!')
        mock_send_email.assert_not_called()

    @patch('utils.send_email.send_link')
    def test_active_user_email(self, mock_send_email):
        data = {'email': 'active_user@gmail.com'}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('errors', response.data)
        self.assertEqual(response.data['errors']['non_field_errors'][0], 'Account already active!')
        mock_send_email.assert_not_called()


class TestChangePasswordAPI(APITestCase):
    def setUp(self):
        self.user = baker.make(User, is_active=True)
        self.user.set_password('kmk13245')
        self.user.save()
        self.token = JWT_token.generate_token(self.user)['token']
        self.url = reverse('users:change_password')
        self.valid_data = {
            'old_password': 'kmk13245',
            'new_password': 'asdF@123',
            'confirm_new_password': 'asdF@123',
        }
        self.invalid_data = {
            'old_password': 'invalid_password',
            'new_password': 'asdF@123',
            'confirm_new_password': 'asdF@123',
        }

    def test_successful_change_password(self):
        response = self.client.put(self.url, data=self.valid_data, HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Your password changed successfully!')
        self.assertTrue(self.user.check_password(self.valid_data['new_password']))

    def test_invalid_old_password(self):
        response = self.client.put(self.url, data=self.invalid_data, HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Your old password is not correct')


class TestSetPasswordAPI(APITestCase):
    def setUp(self):
        self.user = baker.make(User, is_active=True)
        self.token = JWT_token.generate_token(self.user)
        self.url = reverse('users:set_password', args=[self.token['refresh']])

    def test_successful_set_password(self):
        data = {'new_password': 'asdF@123', 'confirm_new_password': 'asdF@123'}
        response = self.client.post(self.url, data)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Password changed successfully')
        self.assertTrue(self.user.check_password(data['new_password']))

    @patch('users.views.get_object_or_404')
    def test_invalid_token_user(self, mock_not_found):
        data = {'new_password': 'asdF@123', 'confirm_new_password': 'asdF@123'}
        mock_not_found.side_effect = Http404
        response = self.client.post(self.url, data)
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Activation link is invalid')
        self.assertFalse(self.user.check_password(data['new_password']))


class TestResetPasswordAPI(APITestCase):
    def setUp(self):
        self.user = baker.make(User, is_active=True, email='email@gmail.com')
        self.url = reverse('users:reset_password')

    def test_successful_reset(self):
        data = {'email': 'email@gmail.com'}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'sent you a change password link!')

    @patch('users.views.get_object_or_404')
    def test_invalid_email(self, mock_get_object):
        mock_get_object.side_effect = Http404
        data = {'email': 'email@gmail.com'}
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'user with this Email not found!')


class TestBlockTokenAPI(APITestCase):
    def setUp(self):
        self.user = baker.make(User, is_active=True)
        self.token = JWT_token.generate_token(self.user)['refresh']
        self.invalid_token = 'invalid.token.alksdjfadffeygfhasjf'
        self.url = reverse('users:token_block')

    @patch('rest_framework_simplejwt.tokens.BlacklistMixin.blacklist')
    def test_successful_block_token(self, mock_black_list):
        data = {'refresh': self.token}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'Token blocked successfully!')
        mock_black_list.assert_called_once()

    def test_block_invalid_token(self):
        data = {'refresh': self.invalid_token}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'token is invalid!')


class TestUserProfileAPI(APITestCase):
    def setUp(self):
        self.user = baker.make(User, is_active=True)
        self.token = JWT_token.generate_token(self.user)['token']

    def test_retrieve_user_profile_GET(self):
        url = reverse('users:user_profile', args=[self.user.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['username'], self.user.username)

    def test_retrieve_user_profile_not_found(self):
        url = reverse('users:user_profile', args=[23])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['detail'], 'No User matches the given query.')

    def test_partial_update_user_profile(self):
        data = {'username': 'new_username'}
        url = reverse('users:user_profile', args=[1])
        response = self.client.patch(url, data, HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.assertEqual(response.status_code, 200)

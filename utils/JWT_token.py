import jwt
from django.conf import settings

from users.serializers import MyTokenObtainPairSerializer


def generate_token(user, lifetime=None):
    token = MyTokenObtainPairSerializer.get_token(user, lifetime)
    return {"refresh": str(token), "token": str(token.access_token)}


def decode_token(token):
    try:
        decoded_data = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return decoded_data['user_id']
    except jwt.ExpiredSignatureError:
        return {'error': 'Activation link has expired!'}
    except jwt.InvalidTokenError:
        return {'error': 'Activation link is invalid!'}

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user, lifetime=None):
        token = super().get_token(user)
        if lifetime:
            token.set_exp(claim='exp', lifetime=lifetime)
        return token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ('password',)
        read_only_fields = ('id', 'last_login', 'is_superuser', 'is_admin', 'groups', 'user_permissions')

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError('fields can not be blank.')
        return attrs

    def validate_username(self, username):
        users = User.objects.filter(username__exact=username)
        if users.exists():
            raise serializers.ValidationError('user with this username already exists.')
        return username

    def validate_email(self, email):
        users = User.objects.filter(email__exact=email)
        if users.exists():
            raise serializers.ValidationError('user with this Email already exists.')
        return email


class UserRegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(required=True, write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8}
        }

    def validate(self, data):
        password1 = data.get('password')
        password2 = data.get('password2')
        if password1 and password2 and password1 != password2:
            raise serializers.ValidationError('Passwords must match.')
        try:
            validate_password(password2)
        except serializers.ValidationError:
            raise serializers.ValidationError()
        return data


class ResendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        email = attrs.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('User does not exist!')
        if user.is_active:
            raise serializers.ValidationError('Account already active!')
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_new_password')
        if new_password and confirm_password and new_password != confirm_password:
            raise serializers.ValidationError('Passwords must match')
        try:
            validate_password(new_password)
        except serializers.ValidationError:
            raise serializers.ValidationError()
        return attrs


class SetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.get('confirm_new_password')
        if new_password and confirm_new_password and new_password != confirm_new_password:
            raise serializers.ValidationError('Passwords must match')
        try:
            validate_password(new_password)
        except serializers.ValidationError:
            raise serializers.ValidationError()
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class TokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True, write_only=True)

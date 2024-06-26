from rest_framework_simplejwt.tokens import RefreshToken
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import status
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from permissions import permissions
from utils import JWT_token, send_email
from .models import User
from .serializers import (UserSerializer,
                          UserRegisterSerializer,
                          ResendVerificationEmailSerializer,
                          ChangePasswordSerializer,
                          TokenSerializer,
                          )


class UsersListAPI(ListAPIView):
    """
    Returns list of users.\n
    allowed methods: GET.
    """
    permission_classes = [IsAdminUser, ]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRegisterAPI(CreateAPIView):
    """
    Registers a User.\n
    allowed methods: POST.
    """
    model = User
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.NotAuthenticated, ]


class UserRegisterVerifyAPI(APIView):
    """
    Verification view for registration.\n
    allowed methods: GET.
    """
    permission_classes = [permissions.NotAuthenticated, ]

    def get(self, request, token):
        user_id = JWT_token.decode_token(token)
        try:
            user = get_object_or_404(User, pk=user_id)
            if user.is_active:
                return Response(data={'message': 'Your account already activated!'}, status=status.HTTP_400_BAD_REQUEST)
            user.is_active = True
            user.save()
            return Response(data={'message': 'Account activated successfully!'})
        except Http404:
            return Response({'message': 'Activation link is invalid!'}, status=status.HTTP_404_NOT_FOUND)
        except TypeError:
            return Response(user_id)


class ResendVerificationEmailAPI(APIView):
    """
    makes a new token and send it with email.\n
    allowed methods: POST.
    """
    permission_classes = [permissions.NotAuthenticated, ]
    serializer_class = ResendVerificationEmailSerializer

    def post(self, request):
        srz_data = self.serializer_class(data=request.POST)
        if srz_data.is_valid():
            user = srz_data.validated_data['user']
            token = JWT_token.generate_token(user)
            url = self.request.build_absolute_uri(
                reverse('users:user_register_verify', kwargs={'token': token['token']})
            )
            send_email.send_link(user.email, url)
            return Response(
                {"message: The activation email has been sent again successfully"},
                status=status.HTTP_200_OK,
            )
        return Response({'errors': srz_data.errors}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordAPI(APIView):
    """
    Changes a user password.\n
    allowed methods: POST.
    """
    permission_classes = [IsAuthenticated, ]
    serializer_class = ChangePasswordSerializer

    def put(self, request):
        srz_data = self.serializer_class(data=request.POST)
        if srz_data.is_valid():
            user = User.objects.get(id=self.request.user.id)
            old_password = srz_data.validated_data['old_password']
            new_password = srz_data.validated_data['new_password']
            if user.check_password(old_password):
                user.set_password(new_password)
                user.save()
                return Response({'message': 'Your password changed successfully!'}, status=status.HTTP_200_OK)
            return Response({'error': 'Your old password is not correct'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': srz_data.errors}, status=status.HTTP_400_BAD_REQUEST)


class BlockTokenAPI(APIView):
    """
    blocks a deleted token
    allowed methods: POST.
    """
    serializer_class = TokenSerializer
    permission_classes = [IsAdminUser, ]

    def post(self, request):
        srz_data = self.serializer_class(data=request.POST)
        if srz_data.is_valid():
            token = RefreshToken(request.POST['refresh'])
            token.blacklist()
            return Response(data={'message': 'Token blocked successfully!'}, status=status.HTTP_200_OK)
        return Response(data={'error': srz_data.errors}, status=status.HTTP_400_BAD_REQUEST)

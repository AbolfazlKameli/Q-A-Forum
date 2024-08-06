from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.urls import reverse

from users.models import User
from utils import JWT_token, send_email


@shared_task
def send_verification_email(email_address, user_id):
    user = User.objects.get(id=user_id)
    token = JWT_token.generate_token(user, timedelta(minutes=1))
    url = f"http://{settings.DOMAIN}{reverse('users:user_register_verify', args=[token['refresh']])}"
    send_email.send_link(email_address, url)

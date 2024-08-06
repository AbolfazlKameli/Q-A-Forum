from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_link(email, link):
    context = {
        'receiver': email,
        'Activation_link': link
    }
    template_name = 'activation_link.html'
    convert_to_html_context = render_to_string(
        template_name=template_name,
        context=context,
    )
    plain_message = strip_tags(convert_to_html_context)
    send_mail(
        subject="Verification URL from AskTech",
        message=plain_message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        html_message=convert_to_html_context,
    )

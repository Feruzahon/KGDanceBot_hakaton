from django.core.mail import send_mail
from celery import shared_task

from decouple import config

HOST = config('HOST_FOR_SEND_MAIL')

@shared_task
def send_activation_email(email, activation_code):
    activation_url = f'{HOST}/account/activate/?u={activation_code}'
    message = f'Активировать: {activation_url}'
    send_mail(
        subject="Активация аккаунта",
        message=message,
        from_email='abdrahmanovtemrilan71@gmail.com',
        recipient_list=[email],
    )

    
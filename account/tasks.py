from django.core.mail import send_mail
from celery import shared_task

from decouple import config

HOST = config('HOST_FOR_SEND_MAIL')

@shared_task
def send_activation_email(email, activation_code):
    activation_url = f'{HOST}/account/activate/?u={activation_code}'
    message = ''
    html = f"""
<h1>Для активации нажмите кнопку</h1>
<a href="{activation_url}">
<button> Нажми сюда </button>
</a>
"""
    send_mail(
        subject="Активация аккаунта",
        message=message,
        from_email='a@gmail.com',
        recipient_list=[email],
        html_message=html
    )
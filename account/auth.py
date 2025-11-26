from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import CustomUser

class TelegramAuthentication(BaseAuthentication):
    def authenticate(self, request):
        telegram_id = request.headers.get('X-Telegram-Id')
        if not telegram_id:
            return None
        try:
            user = CustomUser.objects.get(telegram_id=telegram_id)
        except CustomUser.DoesNotExist:
            raise AuthenticationFailed('User not found')
        
        return (user, None)
        
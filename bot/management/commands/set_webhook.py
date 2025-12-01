from django.core.management.base import BaseCommand
import requests
from django.conf import settings

class Command(BaseCommand):
    help = 'Set Telegram webhook'

    def handle(self, *args, **options):
        url = f"https://api.telegram.org/bot{settings.TG_TOKEN}/setWebhook?url={settings.TELEGRAM_BOT_WEBHOOK_URL}"
        response = requests.get(url)
        if response.status_code == 200:
            self.stdout.write(self.style.SUCCESS('Webhook успешно установлен!'))
        else:
            self.stdout.write(self.style.ERROR(f'Ошибка при установке: {response.text}'))

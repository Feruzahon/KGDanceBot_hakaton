import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'config.settings')

app = Celery('config',)

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

# app.conf.beat_shedule = {
#     "check-subscriptions-every-day":{
#         "task": "subscription.tasks.check_subscriptions_expiry",
#         "shedule":10.0
#     }
# }
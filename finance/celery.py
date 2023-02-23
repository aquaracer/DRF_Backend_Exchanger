import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_exchanger.settings')

app = Celery('backend_exchanger')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.update(
    {
        'task_routes': {
            'send_notification': {'queue': 'send_notification'},
            'update_exchange_rates': {'queue': 'update_exchange_rates'},
        }
    }
)

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update_exchange_rates': {
        'task': 'finance.tasks.update_exchange_rates',
        'schedule': crontab(hour=12, minute=30),
    },
}

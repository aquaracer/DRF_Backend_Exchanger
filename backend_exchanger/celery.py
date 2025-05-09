import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_exchanger.settings')

app = Celery('backend_exchanger')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# Configure Celery Beat schedule
app.conf.beat_schedule = {
    'update-currency-rates': {
        'task': 'finance.tasks.update_currency_rates',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
    'cleanup-old-transactions': {
        'task': 'finance.tasks.cleanup_old_transactions',
        'schedule': crontab(hour=0, minute=0),  # Daily at midnight
    },
}

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}') 
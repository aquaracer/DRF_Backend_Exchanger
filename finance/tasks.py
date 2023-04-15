import os, requests, redis, json, logging
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from .celery import app
from users.models import User
from users.services import advanced_get_request

logger = logging.getLogger('__name__')


@app.task(
    bind=True,
    soft_time_limit=os.getenv('CELERY_TASK_TIMEOUT', 300),
    default_retry_delay=os.getenv('CELERY_TASK_RETRY_TIME', 30),
    queue='send_notification'
)
def send_notification(self, senders_account, receivers_account, amount_to_receive, currency_to_receive):
    """Отправка пользователю смс уведомления о входящем платеже"""

    sender = get_object_or_404(User, account=senders_account)
    receiver = get_object_or_404(User, account=receivers_account)

    if receiver.sms_notification:
        if not receiver.phone:
            raise ObjectDoesNotExist
        message = f"Зачислен перевод на сумму {amount_to_receive}{currency_to_receive} от {sender.first_name}{sender.last_name}"
        url = f"{os.environ.get('SMS_PROVIDER')}&phones={receiver.phone}&mes={message}"
        response = advanced_get_request(url, 3)
        if response['error']:
            return response


@app.task(
    bind=True,
    soft_time_limit=os.getenv('CELERY_TASK_TIMEOUT', 300),
    default_retry_delay=os.getenv('CELERY_TASK_RETRY_TIME', 30),
    queue='update_exchange_rates'
)
def update_exchange_rates(self):
    """Обновление курсов валют"""

    response = advanced_get_request(os.environ.get('CURRENCY_COURSES_URL'), 3)

    if response['error']:
        return response

    redis_instance = redis.StrictRedis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'), db=0)
    rates = json.loads(response['response'].text)

    for currency in ['USD', 'EUR', 'CNY']:
        redis_instance.set(currency, round(rates['Valute'][currency]['Value'], 2))

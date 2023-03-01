import os, requests, redis, json
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from .celery import app
from users.models import User


@app.task(
    bind=True,
    soft_time_limit=os.getenv('CELERY_TASK_TIMEOUT', 300),
    default_retry_delay=os.getenv('CELERY_TASK_RETRY_TIME', 30),
    queue='send_notification'
)
def send_notification(senders_account, receivers_account, amount_to_receive, currency_to_receive):
    """Отправка пользователю смс уведомления о входящем платеже"""

    sender = get_object_or_404(User, account=senders_account)
    receiver = get_object_or_404(User, account=receivers_account)

    if receiver.sms_notification:
        if not receiver.phone:
            raise ObjectDoesNotExist
        message = f"Зачислен перевод на сумму {amount_to_receive}{currency_to_receive} от {sender.first_name}{sender.last_name}"
        url = f"{os.environ.get('SMS_PROVIDER')}&phones={receiver.phone}&mes={message}"
        try:
            response = requests.get(url, timeout=3)
            response.raise_for_status()
        except requests.exceptions.RequestException as err:
            print("Another Error: Something Else", err)
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)


@app.task(bind=True, soft_time_limit=os.getenv('CELERY_TASK_TIMEOUT', 300),
          default_retry_delay=os.getenv('CELERY_TASK_RETRY_TIME', 30), queue='update_exchange_rates')
def update_exchange_rates():
    """Обновление курсов валют"""

    try:  # получаем актуальные курсы валют
        response = requests.get(os.environ.get('CURRENCY_COURSES_URL'), timeout=3)
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        print("Another Error: Something Else", err)
    except requests.exceptions.HTTPError as errh:
        print("Http Error:", errh)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)

    redis_instance = redis.StrictRedis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'), db=0)
    rates = json.loads(response.text)

    for currency in ['USD', 'EUR', 'CNY']:  # записываем обновленные курсы в redis
        redis_instance.set(currency, round(rates['Valute'][currency]['Value'], 2))

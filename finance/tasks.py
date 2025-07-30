import json
import logging
import os
from typing import Any, Optional

import redis

from config import settings
from users.services import get_api_response

from .celery import app

logger = logging.getLogger("__name__")


@app.task(
    bind=True,
    soft_time_limit=os.getenv("CELERY_TASK_TIMEOUT", 300),
    default_retry_delay=os.getenv("CELERY_TASK_RETRY_TIME", 30),
    queue="send_notification",
)
def send_sms_notification_task(self, sms_sender_url: str) -> None:
    """Отправка пользователю смс уведомления о входящем платеже"""
    get_api_response(url=sms_sender_url, timeout=3)


@app.task(
    bind=True,
    soft_time_limit=os.getenv("CELERY_TASK_TIMEOUT", 300),
    default_retry_delay=os.getenv("CELERY_TASK_RETRY_TIME", 30),
    queue="update_exchange_rates",

)
def update_exchange_rates(self) -> Optional[dict[str, Any]]:
    """Обновление курсов валют"""

    response = get_api_response(url=settings.CURRENCY_COURSES_URL, timeout=3)
    redis_storage = redis.StrictRedis(
            host=settings.CACHE_HOST,
            port=settings.CACHE_PORT,
            db=settings.CACHE_DB,
        )

    rates = json.loads(response["response"].text)

    for currency in settings.DEFAULT_CURRENCIES_TO_FETCH:
        redis_storage.set(currency, round(rates["Valute"][currency]["Value"], 2))

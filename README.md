# DRF Backend Exchanger

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0.2-green)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](https://github.com/yourusername/DRF_Backend_Exchanger)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)](https://github.com/yourusername/DRF_Backend_Exchanger)
[![Code Quality](https://img.shields.io/badge/code%20quality-A-brightgreen)](https://github.com/yourusername/DRF_Backend_Exchanger)

Мощный бэкенд на Django REST Framework для платформы обмена валют с продвинутыми функциями и лучшими практиками.

## Скриншоты

### API Документация (Swagger)
![API Documentation](docs/images/swagger.png)

### Мониторинг (Grafana)
![Monitoring Dashboard](docs/images/grafana.png)

### Административная панель
![Admin Panel](docs/images/admin.png)

## Возможности

- 🔐 Безопасная аутентификация с использованием JWT и OAuth2
- 💱 Курсы валют в реальном времени
- 🔄 Асинхронная обработка задач с Celery
- 📊 Метрики Prometheus и мониторинг
- 🐳 Контейнеризация с Docker
- 🧪 Полное покрытие тестами
- 🔍 Документация API с использованием Swagger/OpenAPI
- 📈 Ограничение частоты запросов и кэширование
- 🔒 Лучшие практики безопасности
- 📧 Email-уведомления
- 💳 Интеграция с платежной системой YooKassa

## Технологический стек

- Python 3.9+
- Django 4.2
- Django REST Framework
- PostgreSQL
- Redis
- RabbitMQ
- Celery
- Docker
- Prometheus
- Sentry

## Требования

- Docker и Docker Compose
- Python 3.9+
- PostgreSQL 13+
- Redis 7+
- RabbitMQ

## Быстрый старт

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/DRF_Backend_Exchanger.git
cd DRF_Backend_Exchanger
```

2. Создайте и настройте переменные окружения:
```bash
cp env.example .env
# Отредактируйте .env с вашими настройками
```

3. Запустите сервисы:
```bash
docker-compose up -d
```

4. Выполните миграции:
```bash
docker-compose exec api python manage.py migrate
```

5. Создайте суперпользователя:
```bash
docker-compose exec api python manage.py createsuperuser
```

## Разработка

### Настройка локальной разработки

1. Создайте и активируйте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
.\venv\Scripts\activate  # Windows
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Запустите сервер разработки:
```bash
python manage.py runserver
```

### Запуск тестов

```bash
pytest
```

### Качество кода

```bash
# Форматирование кода
black .
isort .

# Проверка кода
flake8
mypy .

# Запуск тестов с отчетом о покрытии
pytest --cov
```

## Документация API

Документация API доступна по адресам:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

## Мониторинг

- Метрики Prometheus: `http://localhost:8000/metrics`
- Настроено отслеживание ошибок в Sentry

## Участие в разработке

1. Сделайте форк репозитория
2. Создайте ветку для вашей функции (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте ваши изменения (`git commit -m 'Add some amazing feature'`)
4. Отправьте изменения в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## Лицензия

Этот проект распространяется под лицензией MIT - подробности в файле LICENSE.



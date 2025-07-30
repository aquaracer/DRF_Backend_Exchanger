# DRF Backend Exchanger

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0.2-green?logo=django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14%2B-red?logo=django)](https://www.django-rest-framework.org/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16%2B-blue?logo=postgresql)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7%2B-red?logo=redis)](https://redis.io/)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-3.9%2B-orange?logo=rabbitmq)](https://www.rabbitmq.com/)
[![Celery](https://img.shields.io/badge/Celery-5.3-green?logo=celery)](https://docs.celeryq.dev/)
[![YooKassa](https://img.shields.io/badge/YooKassa-API-yellow?logo=yandex)](https://yookassa.ru/)
[![Poetry](https://img.shields.io/badge/Poetry-1.4%2B-60a5fa?logo=poetry)](https://python-poetry.org/)
[![Nginx](https://img.shields.io/badge/Nginx-1.21%2B-green?logo=nginx)](https://nginx.org/)
[![Ruff](https://img.shields.io/badge/linter-ruff-0f172a?logo=python)](https://github.com/astral-sh/ruff)

## Описание проекта

Проект представляет собой **бэкенд-систему для платформы обмена валют** с двумя личными
кабинетами:
**Личный Кабинет Пользователя** и **Личный Кабинет Администратора**.

### 🏠 Личный Кабинет Пользователя

Пользователь авторизуется по логину и паролю, получая JWT токен для доступа к защищенным
эндпоинтам.

#### Функционал:

- Просмотр и редактирование информации о Пользователе;
- Просмотр списка собственных счетов с отоборажение для каждого счета: номера
  счета, валюты счета, баланса;
- Перевод средств между своим счетами и на счет другого пользователя. Если валют
  счета отправителя и счета получателя отличаются - происходит автоматическая
  конвертация средств по текущему курсу в системе. При переводе средств производится
  отправка(в фоновом режиме посредством Celery) смс-уведомления получателю;
- Просмотр списка транзакций с возможностью фильтрации и
  сортировки
- Просмотр текущий курсов валют к рублю: Доллар, Евро, Юани;
- Пополнение счета обменника с банковской карты посредством сервиса YooKassa;
- Просмотр списка заявок на ввод-вывод средств;

### Личный Кабинет Администратора

#### Функционал:

- Отображение списка всех счетов всех пользователей с возможностью фильтрации и
  сортировки;
- Отображение списка всех транзакций всех пользователей с фильтрацией и сортировкой;

## 🚀 Возможности

- 🔐 Безопасная аутентификация (JWT, OAuth2)
- 💱 Автоматическое обновление курсов валют
- 🔄 Асинхронные задачи (Celery, RabbitMQ)
- 🐳 Контейнеризация (Docker Compose)
- 🔍 Документация API (Swagger/OpenAPI, ReDoc)
- 📈 Кэширование (Redis)
- 📧 SMS-уведомления
- 💳 Интеграция с YooKassa API

## 📋 API Эндпоинты

### 🔐 Аутентификация

- `POST /auth/token/login/` - Получение токена аутентификации (требует
  username/password)
- `POST /auth/token/logout/` - Выход из системы (инвалидация токена)

### 👤 ЛК Пользователя (`/api/v1/users/`)

- `POST /api/v1/users/signup` - Регистрация нового пользователя с дополнительной
  информацией
- `GET /api/v1/users/profile/` - Получение профиля пользователя (имя, телефон,
  настройки)
- `PUT /api/v1/users/profile/` - Полное обновление профиля пользователя
- `PATCH /api/v1/users/profile/` - Частичное обновление профиля пользователя

### 💰 Счета в ЛК Пользователя (`/api/v1/users/accounts/`)

- `GET /api/v1/users/accounts/` - Список счетов пользователя с пагинацией

### 💸 Транзакции Пользователя (`/api/v1/users/transactions/`)

- `GET /api/v1/users/transactions/` - Список транзакций пользователя (
  входящие/исходящие)
- `POST /api/v1/users/transactions/transfer_funds/` - Перевод средств между счетами (
  своими или контрагента)

### 📝 Заявки на ввод/вывод ЛК Пользователя (`/api/v1/users/applications/`)

- `GET /api/v1/users/applications/` - Список заявок пользователя на ввод/вывод средств
- `POST /api/v1/users/applications/` - Создание заявки на ввод/вывод средств через
  YooKassa
- `POST /api/v1/users/applications/webhook_handler/` - Обработка вебхука от YooKassa для
  обновления статуса платежа

### 💱 Курсы валют (`/api/v1/finance/`)

- `GET /api/v1/finance/get_rates/` - Получение актуальных курсов валют (RUR, USD, EUR,
  CNY)

### 👨‍💼 Счета пользователей в ЛК Администратора (`/api/v1/admins/accounts/`)

- `GET /api/v1/admins/accounts/` - Список всех счетов пользователей с фильтрацией и
  сортировкой
- `PATCH /api/v1/admins/accounts/{id}/` - Изменение баланса счета пользователя (только
  для админов)

### 👨‍💼 Транзакции пользователей в ЛК Администратора (`/api/v1/admins/transactions/`)

- `GET /api/v1/admins/transactions/` - Список всех транзакций в системе с фильтрацией и
  сортировкой

### 📚 Документация API

- `GET /api/schema/` - OpenAPI схема в JSON формате
- `GET /api/schema/swagger-ui/` - Интерактивный Swagger UI интерфейс

### 🔧 Административная панель

- `GET /admin/` - Django Admin панель для управления данными

---

## 🗂️ Структура проекта

```
DRF_Backend_Exchanger/
├── 📁 admins/                    # Личный Кабинет Администратора
│   ├── 📄 views.py              # API представления админа
│   ├── 📄 urls.py               # URL маршруты админ-панели
│   └── 📁 migrations/           # Миграции базы данных
│
├── 📁 config/                    # Конфигурация Django
│   ├── 📄 settings.py           # Настройки проекта
│   ├── 📄 urls.py               # Главные URL маршруты
│   ├── 📄 celery.py             # Конфигурация Celery
│   └── 📄 wsgi.py               # WSGI конфигурация
│
├── 📁 common/                    # Общие компоненты
│   ├── 📄 models.py             # Базовые модели
│   └── 📄 exceptions.py         # Кастомные исключения
│
├── 📁 finance/                   # Финансовый модуль
│   ├── 📄 models.py             # Модели: Account, Transaction, Currency, Application
│   ├── 📄 views.py              # API представления финансов
│   ├── 📄 serializers.py        # Сериализаторы для API
│   ├── 📄 urls.py               # URL маршруты финансов
│   ├── 📄 filters.py            # Фильтры для списков
│   ├── 📄 pagination.py         # Настройки пагинации
│   ├── 📄 tasks.py              # Celery задачи
│   ├── 📄 signals.py            # Django сигналы
│   ├── 📄 admin.py              # Админ-панель моделей
│   └── 📁 services/             # Бизнес-логика
│       ├── 📄 finance_services.py  # Финансовые операции
│       └── 📄 yookassa.py          # Интеграция с YooKassa
│
├── 📁 users/                     # Личный Кабинет Пользователя
│   ├── 📄 models.py             # Модели: User, UserAdditionalInfo
│   ├── 📄 views.py              # API представления пользователей
│   ├── 📄 serializers.py        # Сериализаторы пользователей
│   ├── 📄 urls.py               # URL маршруты пользователей
│   ├── 📄 services.py           # Сервисы пользователей
│   ├── 📄 admin.py              # Админ-панель пользователей
│   └── 📁 migrations/           # Миграции базы данных
│
├── 📁 nginx/                     # Конфигурация Nginx
│   ├── 📄 default.conf          # Nginx конфигурация
│   └── 📄 Dockerfile            # Dockerfile для Nginx
│
├── 📄 docker-compose.yml         # Docker Compose конфигурация
├── 📄 Dockerfile                 # Dockerfile для Django
├── 📄 manage.py                  # Django management script
├── 📄 pyproject.toml            # Poetry конфигурация
├── 📄 poetry.lock               # Poetry lock файл
├── 📄 env.example               # Пример переменных окружения
└── 📄 README.md                 # Документация проекта
```

## Быстрый старт

### Развертывание с помощью Docker

1. Создайте папку с проектом и склонируйте репозиторий:

```bash
mkdir DRF_Backend_Exchanger
cd DRF_Backend_Exchanger
git clone https://github.com/aquaracer/DRF_Backend_Exchanger.git
```

2. Настройте переменные окружения в файле .env.

3. Соберите и запустите контейнеры:

```bash
docker-compose up --build
```

Приложение будет доступно по следующим адресам:

- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/api/schema/swagger-ui/`
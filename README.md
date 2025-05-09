# DRF Backend Exchanger

A robust Django REST Framework backend for a currency exchange platform with advanced features and best practices.

## Features

- 🔐 Secure authentication with JWT and OAuth2
- 💱 Real-time currency exchange rates
- 🔄 Asynchronous task processing with Celery
- 📊 Prometheus metrics and monitoring
- 🐳 Docker containerization
- 🧪 Comprehensive test coverage
- 🔍 API documentation with Swagger/OpenAPI
- 📈 Rate limiting and caching
- 🔒 Security best practices
- 📧 Email notifications
- 💳 Payment integration with YooKassa

## Tech Stack

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

## Prerequisites

- Docker and Docker Compose
- Python 3.9+
- PostgreSQL 13+
- Redis 7+
- RabbitMQ

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/yourusername/DRF_Backend_Exchanger.git
cd DRF_Backend_Exchanger
```

2. Create and configure environment variables:
```bash
cp env.example .env
# Edit .env with your configuration
```

3. Start the services:
```bash
docker-compose up -d
```

4. Run migrations:
```bash
docker-compose exec api python manage.py migrate
```

5. Create superuser:
```bash
docker-compose exec api python manage.py createsuperuser
```

## Development

### Local Development Setup

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run development server:
```bash
python manage.py runserver
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black .
isort .

# Lint code
flake8
mypy .

# Run tests with coverage
pytest --cov
```

## API Documentation

API documentation is available at:
- Swagger UI: `http://localhost:8000/api/docs/`
- ReDoc: `http://localhost:8000/api/redoc/`

## Monitoring

- Prometheus metrics: `http://localhost:8000/metrics`
- Sentry error tracking is configured

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Security

Please report any security issues to security@yourdomain.com

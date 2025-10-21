# Food Tracker (FdT)

Это сервис для учета питания, воды и активности пользователя (FastAPI + SQLModel). 

## Требования
- Python 3.13+ (рекомендуется)
- Docker + Docker Compose (для быстрого запуска)
- Poetry или pip для локальной разработки


## Быстрый запуск (Docker)
1) Создайте файл `.env` на основе примера (см. раздел ниже).
2) Запустите контейнеры:

```powershell
# собрать и запустить сервисы в фоне
docker compose up --build -d
# или (если у вас старая версия):
docker-compose up --build -d
```

3) Откройте в браузере: http://localhost:8000/docs — Swagger/OpenAPI

## Переменные окружения (.env.example)
Создайте `.env` в корне проекта, пример:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=fooddb
DATABASE_URL=postgresql://postgres:password@db:5432/fooddb
REDIS_URL=redis://redis:6379/0
SECRET_KEY="your-very-secret-key"
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Не храните `SECRET_KEY` в публичных репозиториях. Для продакшн используйте secret manager.

## pre-commit
В репозитории есть `.pre-commit-config.yaml`. Установите и активируйте хуки:

```powershell
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## Основные эндпоинты (быстрый обзор)
В проекте имеются базовые маршруты — проверьте `app/api/v1/`.


## Вклад и контакты
1. Форкните репозиторий.
2. Создайте feature-ветку.
3. Сделайте PR с описанием и тестами.


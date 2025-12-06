# 🚀 Быстрый старт ARIN Platform

## Вариант 1: С Docker (рекомендуется)

### Требования
- Docker Desktop для macOS
- Git

### Установка Docker
1. Скачайте Docker Desktop: https://www.docker.com/products/docker-desktop
2. Установите и запустите Docker Desktop
3. Проверьте: `docker --version`

### Запуск проекта

```bash
# 1. Клонируйте репозиторий (если еще не сделано)
git clone https://github.com/MRsaa1/arin-platform.git
cd arin-platform

# 2. Создайте .env файл
cp .env.example .env
# Отредактируйте .env и установите пароли и API ключи

# 3. Запустите все сервисы
docker-compose up -d

# 4. Проверьте статус
docker-compose ps

# 5. Проверьте логи
docker-compose logs -f backend

# 6. Откройте в браузере
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Health: http://localhost:8000/health
```

## Вариант 2: Локальный запуск (без Docker)

### Требования
- Python 3.10+
- PostgreSQL 15+
- Redis
- Neo4j 5+

### Установка зависимостей

```bash
cd arin-platform/backend
python3 -m venv venv
source venv/bin/activate  # На macOS/Linux
# или
venv\Scripts\activate  # На Windows

pip install -r requirements.txt
```

### Настройка БД

```bash
# PostgreSQL
createdb arin
createdb arin_ts

# Neo4j - установите и запустите Neo4j Desktop
# Redis - установите и запустите Redis
```

### Запуск

```bash
# Установите переменные окружения
export DATABASE_URL="postgresql://arin:dev_password_123@localhost:5432/arin"
export TIMESCALEDB_URL="postgresql://arin:dev_password_123@localhost:5433/arin_ts"
export REDIS_URL="redis://localhost:6379"
export NEO4J_URL="bolt://localhost:7687"
export NEO4J_USER="neo4j"
export NEO4J_PASSWORD="dev_password_123"
export SECRET_KEY="dev_secret_key_change_in_production_12345678901234567890123456789012"

# Запустите backend
cd backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

## Проверка работы

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. API Documentation
Откройте в браузере: http://localhost:8000/docs

### 3. Список агентов
```bash
curl http://localhost:8000/api/v1/agents
```

### 4. Запуск анализа риска
```bash
curl -X POST http://localhost:8000/api/v1/risks/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "type": "credit",
    "entity_id": "test_company_1",
    "entity_type": "company"
  }'
```

## Troubleshooting

### Docker не запускается
- Убедитесь, что Docker Desktop запущен
- Проверьте: `docker ps`

### Порт занят
- Измените порты в `docker-compose.yml`
- Или остановите другие сервисы на портах 8000, 5432, 6379, 7687

### Ошибки подключения к БД
- Проверьте, что все БД запущены
- Проверьте пароли в `.env`
- Проверьте логи: `docker-compose logs postgres`

## Следующие шаги

1. Настройте API ключи (NVIDIA, OpenAI) в `.env`
2. Изучите API документацию: http://localhost:8000/docs
3. Запустите frontend (если нужно): `cd frontend && npm install && npm run dev`


# ARIN Platform - Admin Guide

## Введение

Руководство администратора для управления и настройки ARIN Platform.

## Установка и настройка

### Требования

- Python 3.10+
- PostgreSQL 15+ с TimescaleDB
- Redis 7+
- Neo4j 5+
- Docker & Docker Compose (опционально)

### Установка через Docker

```bash
# Клонирование репозитория
git clone https://github.com/MRsaa1/arin-platform.git
cd arin-platform

# Создание .env файла
cp .env.example .env
# Отредактируйте .env и добавьте ваши ключи

# Запуск
docker-compose up -d
```

### Локальная установка

```bash
# Установка зависимостей
cd backend
pip install -r requirements.txt

# Настройка БД
# Создайте БД и примените миграции

# Запуск
uvicorn backend.main:app --reload
```

## Конфигурация

### Переменные окружения

Основные переменные в `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/arin
TIMESCALEDB_URL=postgresql://user:password@localhost:5433/arin_ts
REDIS_URL=redis://localhost:6379
NEO4J_URL=bolt://localhost:7687

# API Keys
NVIDIA_API_KEY=your-nvidia-api-key
OPENAI_API_KEY=your-openai-api-key

# Security
SECRET_KEY=your-secret-key-change-in-production
```

### Настройка производительности

В `backend/config.py`:
- `pool_size`: Размер пула соединений БД (по умолчанию 20)
- `max_overflow`: Максимальный overflow (по умолчанию 10)
- `access_token_expire_minutes`: Время жизни токена (по умолчанию 30)

## Управление пользователями

### Создание пользователя

Через API:
```bash
POST /api/v1/auth/register
{
  "username": "admin",
  "email": "admin@example.com",
  "password": "secure_password"
}
```

### Назначение ролей

В production роли должны назначаться через БД или admin панель.

Роли:
- `admin`: Полный доступ
- `analyst`: Анализ и просмотр
- `viewer`: Только просмотр
- `api_user`: API доступ

## Управление API ключами

### Создание API ключа

```bash
POST /api/v1/auth/api-keys
Authorization: Bearer <admin_token>
{
  "name": "Integration Key",
  "permissions": ["view_risks", "analyze_risks"],
  "expires_days": 365
}
```

**Важно**: API ключ показывается только один раз! Сохраните его.

### Отзыв API ключа

```bash
DELETE /api/v1/auth/api-keys/{key_id}
Authorization: Bearer <admin_token>
```

## Мониторинг

### Health Check

```bash
GET /health
```

Проверяет:
- Подключение к БД
- Подключение к Redis
- Подключение к Neo4j
- Статус агентов

### Performance Metrics

```bash
GET /api/v1/performance/health
Authorization: Bearer <token>
```

Метрики:
- Health score
- Request statistics (p50, p95, p99)
- Agent performance
- Cache statistics

### Audit Logs

```bash
GET /api/v1/compliance/audit-logs?user_id=user123&limit=100
Authorization: Bearer <admin_token>
```

## Backup и Recovery

### Создание бэкапа

```bash
POST /api/v1/compliance/backup
Authorization: Bearer <admin_token>
{
  "backup_type": "full",
  "include_data": true,
  "include_models": true,
  "include_logs": false
}
```

### Список бэкапов

```bash
GET /api/v1/compliance/backup
Authorization: Bearer <admin_token>
```

### Восстановление

```bash
POST /api/v1/compliance/backup/{backup_id}/restore
Authorization: Bearer <admin_token>
{
  "components": ["database", "ml_models"]
}
```

## Data Retention

### Просмотр политик

```bash
GET /api/v1/compliance/retention/policies
Authorization: Bearer <admin_token>
```

### Очистка старых данных

```bash
POST /api/v1/compliance/retention/cleanup?dry_run=false
Authorization: Bearer <admin_token>
```

## Масштабирование

### Docker Swarm

```bash
# Инициализация Swarm
docker swarm init

# Deploy
docker stack deploy -c docker-compose.prod.yml arin-platform

# Масштабирование
docker service scale arin-platform_backend=5
```

### Kubernetes

```bash
# Применение манифестов
kubectl apply -f infrastructure/kubernetes/deployment.yaml
kubectl apply -f infrastructure/kubernetes/celery-worker.yaml

# Проверка
kubectl get deployments
kubectl get hpa
```

## Обслуживание

### Обновление моделей

```bash
# Обучение новой модели
POST /api/v1/ml/train
Authorization: Bearer <admin_token>
# Загрузите CSV файл с данными
```

### Переобучение моделей

Автоматически выполняется каждый день в 2:00 через Celery.

Вручную:
```bash
python backend/scripts/auto_retrain_models.py
```

### Очистка кэша

```bash
POST /api/v1/performance/cache/clear
Authorization: Bearer <admin_token>
```

## Безопасность

### Ротация секретов

1. Обновите `SECRET_KEY` в `.env`
2. Перезапустите приложение
3. Пользователям нужно будет войти заново

### Обновление API ключей

Рекомендуется ротировать API ключи каждые 90 дней.

### TLS/SSL

Настройте Nginx с SSL сертификатами:
```bash
# Используйте nginx-ssl.conf
# Добавьте сертификаты в /etc/nginx/ssl/
```

## Troubleshooting

### Проблемы с БД

```bash
# Проверка подключения
psql -h localhost -U arin_user -d arin_db

# Проверка TimescaleDB
SELECT * FROM timescaledb_information.hypertables;
```

### Проблемы с Redis

```bash
# Проверка подключения
redis-cli ping

# Проверка кэша
redis-cli INFO stats
```

### Проблемы с Neo4j

```bash
# Проверка подключения
cypher-shell -u neo4j -p password
```

### Логи

```bash
# Backend логи
docker logs arin-backend

# Celery логи
docker logs arin-celery-worker

# Nginx логи
docker logs arin-nginx
```

## Best Practices

1. **Регулярные бэкапы**: Ежедневные автоматические бэкапы
2. **Мониторинг**: Отслеживайте health score и метрики
3. **Обновления**: Регулярно обновляйте зависимости
4. **Безопасность**: Ротируйте ключи и пароли
5. **Масштабирование**: Масштабируйте горизонтально при росте нагрузки

## Поддержка

- Email: admin@arin-platform.com
- Документация: https://github.com/MRsaa1/arin-platform
- Issues: https://github.com/MRsaa1/arin-platform/issues


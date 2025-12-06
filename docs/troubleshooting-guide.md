# ARIN Platform - Troubleshooting Guide

## Общие проблемы

### Проблема: API возвращает 503 Service Unavailable

**Причина**: Один из сервисов не запущен или недоступен.

**Решение**:
1. Проверьте health endpoint: `GET /health`
2. Проверьте логи: `docker logs arin-backend`
3. Проверьте подключение к БД:
   ```bash
   psql -h localhost -U arin_user -d arin_db
   ```
4. Проверьте Redis: `redis-cli ping`
5. Проверьте Neo4j: `curl http://localhost:7474`

### Проблема: Медленные запросы

**Причина**: Высокая нагрузка или проблемы с БД.

**Решение**:
1. Проверьте метрики производительности: `GET /api/v1/performance/health`
2. Проверьте использование ресурсов: `docker stats`
3. Проверьте индексы БД:
   ```sql
   SELECT * FROM pg_indexes WHERE tablename = 'risk_analyses';
   ```
4. Очистите кэш: `POST /api/v1/performance/cache/clear`
5. Масштабируйте backend: `docker service scale arin-platform_backend=3`

### Проблема: Ошибки аутентификации

**Причина**: Неверный токен или истекший токен.

**Решение**:
1. Проверьте формат токена: `Bearer <token>`
2. Проверьте срок действия токена
3. Получите новый токен: `POST /api/v1/auth/login`
4. Проверьте SECRET_KEY в конфигурации

### Проблема: Агенты не запускаются

**Причина**: Проблемы с инициализацией или зависимостями.

**Решение**:
1. Проверьте статус агентов: `GET /api/v1/agents`
2. Проверьте логи: `docker logs arin-backend | grep agent`
3. Проверьте подключение к БД и внешним сервисам
4. Перезапустите агента: `POST /api/v1/agents/{agent_id}/restart`

### Проблема: Ошибки при анализе рисков

**Причина**: Недостаточно данных или проблемы с ML моделями.

**Решение**:
1. Проверьте наличие данных для сущности
2. Проверьте статус ML моделей: `GET /api/v1/ml/training-history`
3. Переобучите модель: `POST /api/v1/ml/train`
4. Проверьте логи агента

## Проблемы с БД

### Проблема: Подключение к PostgreSQL

**Ошибка**: `could not connect to server`

**Решение**:
```bash
# Проверка статуса
docker ps | grep postgres

# Проверка подключения
psql -h localhost -U arin_user -d arin_db

# Проверка переменных окружения
echo $DATABASE_URL
```

### Проблема: TimescaleDB не работает

**Ошибка**: `extension "timescaledb" does not exist`

**Решение**:
```sql
-- Подключение к БД
\c arin_ts

-- Создание extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Проверка
SELECT * FROM timescaledb_information.hypertables;
```

### Проблема: Медленные запросы к БД

**Решение**:
1. Проверьте индексы:
   ```sql
   EXPLAIN ANALYZE SELECT * FROM risk_analyses WHERE entity_id = 'AAPL';
   ```
2. Создайте недостающие индексы (см. `backend/database/indexes.py`)
3. Оптимизируйте запросы
4. Увеличьте pool size в конфигурации

## Проблемы с Redis

### Проблема: Redis недоступен

**Ошибка**: `Connection refused`

**Решение**:
```bash
# Проверка статуса
docker ps | grep redis

# Проверка подключения
redis-cli ping

# Проверка переменных окружения
echo $REDIS_URL
```

### Проблема: Кэш не работает

**Решение**:
1. Проверьте подключение к Redis
2. Проверьте статистику кэша: `GET /api/v1/performance/cache/stats`
3. Очистите кэш: `POST /api/v1/performance/cache/clear`
4. Проверьте логи: `docker logs arin-backend | grep cache`

## Проблемы с Neo4j

### Проблема: Neo4j недоступен

**Ошибка**: `Unable to connect`

**Решение**:
```bash
# Проверка статуса
docker ps | grep neo4j

# Проверка подключения
cypher-shell -u neo4j -p password

# Проверка переменных окружения
echo $NEO4J_URL
```

## Проблемы с Celery

### Проблема: Задачи не выполняются

**Решение**:
1. Проверьте статус worker: `celery -A backend.tasks.celery_app inspect active`
2. Проверьте подключение к Redis
3. Проверьте логи: `docker logs arin-celery-worker`
4. Перезапустите worker

### Проблема: Периодические задачи не запускаются

**Решение**:
1. Проверьте статус beat: `docker logs arin-celery-beat`
2. Проверьте расписание в `celery_app.py`
3. Убедитесь, что beat запущен: `docker ps | grep celery-beat`

## Проблемы с производительностью

### Проблема: Высокое использование CPU

**Решение**:
1. Проверьте активные задачи: `GET /api/v1/performance/health`
2. Ограничьте concurrent requests через Nginx
3. Масштабируйте горизонтально
4. Оптимизируйте запросы к БД

### Проблема: Высокое использование памяти

**Решение**:
1. Проверьте размер кэша Redis
2. Ограничьте размер пула соединений БД
3. Проверьте утечки памяти в коде
4. Увеличьте память серверов

### Проблема: Медленные ответы API

**Решение**:
1. Используйте кэширование для частых запросов
2. Оптимизируйте запросы к БД
3. Используйте асинхронный режим для длительных операций
4. Масштабируйте backend

## Проблемы с безопасностью

### Проблема: Ошибки JWT токенов

**Решение**:
1. Проверьте SECRET_KEY в конфигурации
2. Убедитесь, что токен не истек
3. Проверьте формат токена
4. Получите новый токен

### Проблема: Ошибки доступа (403)

**Решение**:
1. Проверьте роли пользователя: `GET /api/v1/auth/me`
2. Убедитесь, что у пользователя есть необходимые разрешения
3. Обратитесь к администратору для назначения ролей

## Проблемы с ML моделями

### Проблема: Модель не обучена

**Решение**:
```bash
# Обучение модели
python backend/scripts/train_credit_risk_model.py

# Или через API
POST /api/v1/ml/train
```

### Проблема: Низкая точность модели

**Решение**:
1. Проверьте качество данных
2. Увеличьте количество данных для обучения
3. Настройте гиперпараметры модели
4. Переобучите модель

## Логи и отладка

### Просмотр логов

```bash
# Backend
docker logs arin-backend -f

# Celery Worker
docker logs arin-celery-worker -f

# Celery Beat
docker logs arin-celery-beat -f

# Nginx
docker logs arin-nginx -f
```

### Уровни логирования

Настройте в `.env`:
```bash
LOG_LEVEL=DEBUG  # Для отладки
LOG_LEVEL=INFO   # Для production
```

## Получение помощи

Если проблема не решена:

1. Проверьте документацию
2. Проверьте Issues на GitHub
3. Создайте новый Issue с деталями:
   - Описание проблемы
   - Шаги для воспроизведения
   - Логи
   - Версия системы
4. Обратитесь в поддержку: support@arin-platform.com


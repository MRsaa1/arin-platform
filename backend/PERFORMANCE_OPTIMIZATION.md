# ARIN Platform - Performance Optimization

## Обзор

Система оптимизации производительности для ARIN Platform включает:
- Connection pooling для БД
- Redis кэширование
- Асинхронная обработка через Celery
- Мониторинг производительности

## Компоненты

### 1. Database Connection Pool

**Файл**: `backend/database/connection_pool.py`

Управление пулом соединений с БД:
- Пул размером 20 соединений
- Максимальный overflow: 10
- Автоматическая проверка соединений (pool_pre_ping)
- Async/await поддержка

**Использование**:
```python
from backend.database import db_pool

async with db_pool.get_session() as session:
    result = await session.execute(query)
```

### 2. Database Indexes

**Файл**: `backend/database/indexes.py`

Индексы для оптимизации запросов:
- Индексы для `risk_analyses` (entity_id, agent_id, timestamp)
- Индексы для `graph_nodes` (node_type, risk_score)
- Индексы для `graph_edges` (source_id, target_id)
- Композитные индексы для частых запросов

**Создание индексов**:
```python
from backend.database import create_indexes

await create_indexes(engine)
```

### 3. Cache Service

**Файл**: `backend/services/cache_service.py`

Redis кэширование:
- Кэширование результатов запросов
- TTL для автоматического истечения
- Поддержка pickle для сложных объектов
- Паттерн get-or-set

**Использование**:
```python
from backend.services import cache_service

# Получение из кэша
value = await cache_service.get("key")

# Установка в кэш
await cache_service.set("key", value, ttl=3600)

# Get or set
value = await cache_service.get_or_set(
    "key",
    lambda: compute_expensive_value(),
    ttl=3600
)
```

### 4. Performance Monitor

**Файл**: `backend/services/performance_monitor.py`

Мониторинг производительности:
- Отслеживание времени выполнения запросов
- Метрики производительности агентов
- Статистика запросов (p50, p95, p99)
- Health score системы

**API Endpoints**:
- `GET /api/v1/performance/health` - Здоровье системы
- `GET /api/v1/performance/requests` - Статистика запросов
- `GET /api/v1/performance/agents` - Производительность агентов
- `GET /api/v1/performance/cache/stats` - Статистика кэша

### 5. Celery Tasks

**Файлы**: 
- `backend/tasks/celery_app.py`
- `backend/tasks/risk_analysis_tasks.py`
- `backend/tasks/model_training_tasks.py`

Асинхронная обработка:
- Фоновые задачи для анализа рисков
- Пакетная обработка
- Автоматическое переобучение моделей
- Периодические задачи (обновление графа, очистка данных)

**Периодические задачи**:
- Обновление графа: каждые 5 минут
- Переобучение моделей: каждый день в 2:00
- Очистка старых данных: каждый день в 3:00

**Использование**:
```python
from backend.tasks.risk_analysis_tasks import analyze_risk_async

# Асинхронное выполнение
task = analyze_risk_async.delay(task_data)

# Проверка статуса
from backend.api.routes.tasks import get_task_status
status = await get_task_status(task.id)
```

## Конфигурация

### Redis

В `.env`:
```
REDIS_URL=redis://localhost:6379/0
```

### Celery Worker

Запуск worker:
```bash
celery -A backend.tasks.celery_app worker --loglevel=info
```

Запуск beat scheduler:
```bash
celery -A backend.tasks.celery_app beat --loglevel=info
```

## Метрики производительности

### Целевые показатели

- Время ответа API < 500ms для стандартных запросов
- Система может обработать 1000+ запросов/минуту
- Кэширование снижает нагрузку на БД на 70%+

### Мониторинг

Используйте Performance Monitor API для отслеживания:
- Среднее время ответа (p50, p95, p99)
- Процент успешных запросов
- Health score системы
- Производительность агентов

## Оптимизация запросов

### Query Optimization

Используйте `analyze_query_performance` для анализа:
```python
from backend.database import analyze_query_performance

result = await analyze_query_performance(engine, query)
print(result["explain"])
```

### Кэширование

Кэшируйте:
- Результаты анализа агентов (TTL: 1 час)
- Данные графа (TTL: 30 минут)
- LLM ответы (TTL: 24 часа)
- Часто запрашиваемые метрики (TTL: 5 минут)

## Best Practices

1. **Используйте connection pooling** для всех запросов к БД
2. **Кэшируйте частые запросы** через Cache Service
3. **Используйте async_mode** для длительных операций
4. **Мониторьте производительность** через Performance Monitor API
5. **Создавайте индексы** для частых запросов
6. **Используйте batch processing** для больших объемов данных


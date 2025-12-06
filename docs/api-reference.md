# ARIN Platform - API Reference

## Base URL

- Development: `http://localhost:8000`
- Production: `https://api.arin-platform.com`

## Аутентификация

Большинство endpoints требуют JWT токен в заголовке:

```
Authorization: Bearer <token>
```

Получите токен через `/api/v1/auth/login`.

## Endpoints

### Health

#### GET /health

Проверка здоровья системы.

**Response**:
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "neo4j": "connected"
}
```

### Authentication

#### POST /api/v1/auth/register

Регистрация нового пользователя.

**Request**:
```json
{
  "username": "user",
  "email": "user@example.com",
  "password": "password",
  "full_name": "User Name"
}
```

**Response**: `Token`

#### POST /api/v1/auth/login

Вход пользователя (OAuth2 password flow).

**Request**: Form data
```
username=user&password=password
```

**Response**: `Token`

#### GET /api/v1/auth/me

Информация о текущем пользователе.

**Headers**: `Authorization: Bearer <token>`

**Response**:
```json
{
  "username": "user",
  "user_id": "user123",
  "roles": ["analyst"]
}
```

### Agents

#### GET /api/v1/agents

Список всех агентов.

**Response**:
```json
{
  "agents": [
    {
      "agent_id": "credit_risk_agent",
      "status": "active",
      "type": "credit_risk"
    }
  ]
}
```

#### GET /api/v1/agents/{agent_id}/status

Статус конкретного агента.

**Response**:
```json
{
  "agent_id": "credit_risk_agent",
  "status": "active",
  "tasks_completed": 150,
  "tasks_failed": 2
}
```

#### POST /api/v1/agents/{agent_id}/start

Запуск агента.

#### POST /api/v1/agents/{agent_id}/stop

Остановка агента.

### Risks

#### POST /api/v1/risks/analyze

Запуск анализа риска.

**Request**:
```json
{
  "type": "credit_analysis",
  "entity_id": "AAPL",
  "entity_type": "company",
  "parameters": {}
}
```

**Query Parameters**:
- `async_mode` (bool): Асинхронное выполнение

**Response**: `RiskAnalysisResponse`

#### GET /api/v1/risks/current

Текущие риски.

**Query Parameters**:
- `entity_id` (str): Фильтр по сущности
- `agent_id` (str): Фильтр по агенту

### Graph

#### GET /api/v1/graph/visualization

Визуализация графа.

**Query Parameters**:
- `max_nodes` (int): Максимальное количество узлов
- `node_filter` (list): Фильтр узлов
- `include_clusters` (bool): Включить кластеры

**Response**:
```json
{
  "nodes": [...],
  "edges": [...],
  "clusters": {...}
}
```

#### POST /api/v1/graph/paths

Поиск путей влияния.

**Request**:
```json
{
  "source_id": "AAPL",
  "target_id": "MSFT",
  "max_depth": 3
}
```

#### GET /api/v1/graph/clusters

Обнаружение кластеров.

**Query Parameters**:
- `method` (str): Метод кластеризации (louvain)

#### GET /api/v1/graph/hotspots

Поиск "горячих точек" риска.

**Query Parameters**:
- `top_n` (int): Количество точек

### Alerts

#### GET /api/v1/alerts

Список алертов.

**Query Parameters**:
- `severity` (str): Фильтр по серьезности
- `status` (str): Фильтр по статусу
- `entity_id` (str): Фильтр по сущности

#### POST /api/v1/alerts

Создание алерта.

**Request**:
```json
{
  "title": "High Risk",
  "message": "Risk increased",
  "severity": "high",
  "entity_id": "AAPL"
}
```

### LLM

#### POST /api/v1/llm/generate

Генерация текста с помощью LLM.

**Request**:
```json
{
  "prompt": "Analyze credit risk",
  "system_message": "You are a financial analyst",
  "model_preference": ["deepseek-r1", "gpt-4"]
}
```

#### POST /api/v1/llm/extract

Извлечение структурированных данных.

**Request**:
```json
{
  "text": "Company has risk score 7.5",
  "schema": {
    "risk_score": "float",
    "factors": "list[str]"
  }
}
```

### ML Models

#### POST /api/v1/ml/train

Обучение модели.

**Request**: Multipart form data с CSV файлом

**Query Parameters**:
- `model_name` (str): Имя модели
- `test_size` (float): Доля тестовых данных
- `retrain` (bool): Переобучение

#### GET /api/v1/ml/training-history

История обучения.

**Query Parameters**:
- `model_name` (str): Фильтр по модели
- `days` (int): Количество дней

### Performance

#### GET /api/v1/performance/health

Здоровье системы.

**Response**:
```json
{
  "health_score": 0.95,
  "status": "healthy",
  "request_statistics": {...},
  "agent_performance": {...}
}
```

#### GET /api/v1/performance/requests

Статистика запросов.

**Query Parameters**:
- `request_type` (str): Тип запроса
- `hours` (int): Количество часов

#### GET /api/v1/performance/cache/stats

Статистика кэша.

### Compliance

#### GET /api/v1/compliance/audit-logs

Audit логи.

**Query Parameters**:
- `user_id` (str): Фильтр по пользователю
- `event_type` (str): Тип события
- `start_date` (datetime): Начальная дата
- `end_date` (datetime): Конечная дата
- `limit` (int): Лимит результатов

#### GET /api/v1/compliance/gdpr/data

Получение данных пользователя (GDPR).

#### DELETE /api/v1/compliance/gdpr/data

Удаление данных пользователя (GDPR).

#### GET /api/v1/compliance/gdpr/export

Экспорт данных пользователя (GDPR).

**Query Parameters**:
- `format` (str): Формат (json, csv)

#### POST /api/v1/compliance/backup

Создание бэкапа.

**Request**:
```json
{
  "backup_type": "full",
  "include_data": true,
  "include_models": true
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
  "detail": "Permission 'analyze_risks' required"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

- 100 requests/second per IP
- 10 concurrent connections per IP

## OpenAPI Documentation

Интерактивная документация доступна по адресу:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`


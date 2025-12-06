# ARIN Platform - User Guide

## Введение

ARIN Platform - это комплексная система управления рисками на основе Agentic AI, которая использует 6 специализированных агентов для анализа различных типов рисков.

## Быстрый старт

### 1. Регистрация и вход

#### Регистрация
```bash
POST /api/v1/auth/register
{
  "username": "analyst",
  "email": "analyst@example.com",
  "password": "secure_password",
  "full_name": "John Analyst"
}
```

#### Вход
```bash
POST /api/v1/auth/login
# OAuth2 password flow
username=analyst&password=secure_password
```

Ответ:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### 2. Использование токена

Добавьте токен в заголовок Authorization:
```bash
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Основные функции

### Анализ рисков

#### Запуск анализа кредитного риска
```bash
POST /api/v1/risks/analyze
Authorization: Bearer <token>
{
  "type": "credit_analysis",
  "entity_id": "AAPL",
  "entity_type": "company",
  "parameters": {
    "include_news": true,
    "include_financials": true
  }
}
```

#### Асинхронный анализ
```bash
POST /api/v1/risks/analyze?async_mode=true
# Возвращает task_id для отслеживания
```

#### Получение результатов
```bash
GET /api/v1/tasks/{task_id}
Authorization: Bearer <token>
```

### Работа с агентами

#### Список агентов
```bash
GET /api/v1/agents
Authorization: Bearer <token>
```

#### Статус агента
```bash
GET /api/v1/agents/{agent_id}/status
Authorization: Bearer <token>
```

#### Запуск агента
```bash
POST /api/v1/agents/{agent_id}/start
Authorization: Bearer <token>
```

### Визуализация графа зависимостей

#### Получение графа
```bash
GET /api/v1/graph/visualization?max_nodes=100
Authorization: Bearer <token>
```

#### Поиск путей влияния
```bash
POST /api/v1/graph/paths
Authorization: Bearer <token>
{
  "source_id": "AAPL",
  "target_id": "MSFT",
  "max_depth": 3
}
```

#### Обнаружение кластеров
```bash
GET /api/v1/graph/clusters?method=louvain
Authorization: Bearer <token>
```

### Работа с алертами

#### Получение алертов
```bash
GET /api/v1/alerts?severity=high&status=active
Authorization: Bearer <token>
```

#### Создание алерта
```bash
POST /api/v1/alerts
Authorization: Bearer <token>
{
  "title": "High Risk Detected",
  "message": "Credit risk increased for AAPL",
  "severity": "high",
  "entity_id": "AAPL"
}
```

### Использование LLM

#### Генерация текста
```bash
POST /api/v1/llm/generate
Authorization: Bearer <token>
{
  "prompt": "Analyze the credit risk for Apple Inc.",
  "system_message": "You are a financial analyst",
  "model_preference": ["deepseek-r1", "gpt-4"]
}
```

#### Извлечение структурированных данных
```bash
POST /api/v1/llm/extract
Authorization: Bearer <token>
{
  "text": "Apple Inc. has a credit risk score of 7.5...",
  "schema": {
    "company_name": "str",
    "credit_risk_score": "float",
    "key_factors": "list[str]"
  }
}
```

## Роли и разрешения

### Viewer (Просмотр)
- Просмотр агентов
- Просмотр рисков
- Просмотр графа
- Просмотр алертов

### Analyst (Аналитик)
- Все права Viewer
- Запуск анализа рисков
- Обучение моделей
- Просмотр метрик производительности

### Admin (Администратор)
- Все права Analyst
- Управление агентами
- Управление пользователями
- Управление системой
- Доступ к compliance функциям

## GDPR - Права пользователей

### Получение своих данных
```bash
GET /api/v1/compliance/gdpr/data
Authorization: Bearer <token>
```

### Экспорт данных
```bash
GET /api/v1/compliance/gdpr/export?format=json
Authorization: Bearer <token>
```

### Удаление данных
```bash
DELETE /api/v1/compliance/gdpr/data
Authorization: Bearer <token>
```

## Примеры использования

### Полный цикл анализа риска

1. **Запуск анализа**:
```bash
POST /api/v1/risks/analyze
{
  "type": "comprehensive_analysis",
  "entity_id": "AAPL",
  "entity_type": "company"
}
```

2. **Проверка статуса**:
```bash
GET /api/v1/risks/current?entity_id=AAPL
```

3. **Просмотр графа зависимостей**:
```bash
GET /api/v1/graph/visualization?node_filter=AAPL
```

4. **Проверка алертов**:
```bash
GET /api/v1/alerts?entity_id=AAPL
```

## Советы и рекомендации

1. **Используйте асинхронный режим** для длительных операций
2. **Кэшируйте результаты** для часто запрашиваемых данных
3. **Мониторьте производительность** через `/api/v1/performance/health`
4. **Используйте фильтры** для оптимизации запросов к графу
5. **Проверяйте алерты** регулярно для раннего обнаружения рисков

## Обработка ошибок

### Типичные ошибки

**401 Unauthorized**
- Проверьте токен в заголовке Authorization
- Убедитесь, что токен не истек

**403 Forbidden**
- У вас нет необходимых разрешений
- Обратитесь к администратору

**404 Not Found**
- Ресурс не существует
- Проверьте правильность ID

**500 Internal Server Error**
- Внутренняя ошибка сервера
- Проверьте логи или обратитесь в поддержку

## Поддержка

- Email: support@arin-platform.com
- Документация: https://github.com/MRsaa1/arin-platform
- Issues: https://github.com/MRsaa1/arin-platform/issues


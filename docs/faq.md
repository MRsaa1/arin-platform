# ARIN Platform - FAQ

## Общие вопросы

### Что такое ARIN Platform?

ARIN Platform - это комплексная система управления рисками на основе Agentic AI, которая использует 6 специализированных агентов для анализа кредитных, рыночных, операционных, ликвидных, регуляторных и системных рисков.

### Какие технологии используются?

- **Backend**: FastAPI, Python 3.10+
- **AI/ML**: DeepSeek R1, GPT-4, XGBoost, PyTorch Geometric
- **Databases**: PostgreSQL, TimescaleDB, Neo4j, Redis
- **Task Queue**: Celery
- **Deployment**: Docker, Kubernetes

### Какие системные требования?

Минимум:
- 2 CPU cores
- 4GB RAM
- 20GB disk space

Рекомендуется:
- 4 CPU cores
- 8GB RAM
- 50GB disk space

## Аутентификация и авторизация

### Как получить токен доступа?

```bash
POST /api/v1/auth/login
username=your_username&password=your_password
```

### Как долго действует токен?

По умолчанию 30 минут. Можно настроить через `ACCESS_TOKEN_EXPIRE_MINUTES` в конфигурации.

### Как обновить токен?

Получите новый токен через `/api/v1/auth/login`.

### Какие роли доступны?

- **Admin**: Полный доступ ко всем функциям
- **Analyst**: Анализ рисков и просмотр данных
- **Viewer**: Только просмотр
- **API User**: API доступ для интеграций

## Анализ рисков

### Как запустить анализ риска?

```bash
POST /api/v1/risks/analyze
{
  "type": "credit_analysis",
  "entity_id": "AAPL",
  "entity_type": "company"
}
```

### Сколько времени занимает анализ?

Зависит от типа анализа:
- Простой анализ: 5-10 секунд
- Комплексный анализ: 30-60 секунд
- Асинхронный режим: возвращает task_id сразу

### Как проверить статус анализа?

```bash
GET /api/v1/tasks/{task_id}
```

### Какие типы анализа доступны?

- `credit_analysis`: Кредитный риск
- `market_analysis`: Рыночный риск
- `operational_analysis`: Операционный риск
- `liquidity_analysis`: Риск ликвидности
- `regulatory_analysis`: Регуляторный риск
- `systemic_analysis`: Системный риск
- `comprehensive_analysis`: Комплексный анализ всех типов

## Агенты

### Сколько агентов в системе?

6 специализированных агентов:
1. Credit Risk Agent
2. Market Risk Agent
3. Operational Risk Agent
4. Liquidity Risk Agent
5. Regulatory Risk Agent
6. Systemic Risk Agent

### Как запустить агента?

```bash
POST /api/v1/agents/{agent_id}/start
```

### Как остановить агента?

```bash
POST /api/v1/agents/{agent_id}/stop
```

## Граф зависимостей

### Что такое граф зависимостей?

Граф показывает взаимосвязи между финансовыми сущностями (компании, секторы, рынки) и позволяет анализировать каскадные эффекты.

### Как визуализировать граф?

```bash
GET /api/v1/graph/visualization?max_nodes=100
```

### Как найти пути влияния?

```bash
POST /api/v1/graph/paths
{
  "source_id": "AAPL",
  "target_id": "MSFT",
  "max_depth": 3
}
```

## ML модели

### Какие ML модели используются?

- **Credit Risk**: XGBoost для предсказания дефолта
- **Systemic Risk**: GNN (Graph Neural Network) для анализа графа

### Как обучить модель?

```bash
POST /api/v1/ml/train
# Загрузите CSV файл с данными
```

### Как часто переобучаются модели?

Автоматически каждый день в 2:00. Также можно запустить вручную.

## Производительность

### Какая производительность системы?

- Response time < 500ms для стандартных запросов
- 1000+ requests/minute
- 70%+ снижение нагрузки на БД через кэширование

### Как проверить производительность?

```bash
GET /api/v1/performance/health
```

### Как оптимизировать производительность?

1. Используйте кэширование
2. Используйте асинхронный режим для длительных операций
3. Масштабируйте горизонтально
4. Оптимизируйте запросы к БД

## Безопасность

### Где хранятся секреты?

В переменных окружения (`.env` файл) или в secrets manager (HashiCorp Vault, AWS Secrets Manager) в production.

### Как ротировать API ключи?

```bash
DELETE /api/v1/auth/api-keys/{old_key_id}
POST /api/v1/auth/api-keys
# Создайте новый ключ
```

### Поддерживается ли GDPR?

Да, реализованы все основные требования GDPR:
- Right of access (Article 15)
- Right to be forgotten (Article 17)
- Data portability (Article 20)

## Compliance

### Как получить audit логи?

```bash
GET /api/v1/compliance/audit-logs
Authorization: Bearer <admin_token>
```

### Как экспортировать audit логи?

```bash
GET /api/v1/compliance/audit-logs/export?start_date=2024-01-01&end_date=2024-12-31&format=json
```

### Какие политики хранения данных?

- Financial Data: 7 лет
- Risk Analyses: 5 лет
- Audit Logs: 3 года
- ML Models: 2 года
- Performance Metrics: 1 год

## Развертывание

### Как развернуть в production?

См. [Deployment Guide](deployment-guide.md)

### Поддерживается ли Kubernetes?

Да, есть готовые манифесты в `infrastructure/kubernetes/`.

### Поддерживается ли Docker Swarm?

Да, есть конфигурация в `docker-compose.prod.yml`.

## Поддержка

### Где получить помощь?

- Email: support@arin-platform.com
- GitHub Issues: https://github.com/MRsaa1/arin-platform/issues
- Документация: https://github.com/MRsaa1/arin-platform

### Как сообщить о баге?

Создайте Issue на GitHub с:
- Описанием проблемы
- Шагами для воспроизведения
- Логами
- Версией системы

### Как предложить новую функцию?

Создайте Issue на GitHub с описанием функции и обоснованием.


# ARIN Platform - Scaling and Load Testing

## Обзор

Система масштабирования и нагрузочного тестирования для ARIN Platform включает:
- Docker Swarm конфигурацию для горизонтального масштабирования
- Kubernetes манифесты с auto-scaling
- Nginx load balancer
- Скрипты для load testing и stress testing
- Инструменты для анализа узких мест

## Docker Swarm

### Конфигурация

**Файл**: `docker-compose.prod.yml`

Особенности:
- Backend API: 3 реплики (scalable)
- Celery Worker: 2 реплики
- Celery Beat: 1 реплика
- Health checks для всех сервисов
- Resource limits для контроля ресурсов
- Overlay network для Swarm

### Запуск

```bash
# Инициализация Swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml arin-platform

# Масштабирование backend
docker service scale arin-platform_backend=5

# Проверка статуса
docker service ls
```

## Kubernetes

### Deployment

**Файлы**:
- `infrastructure/kubernetes/deployment.yaml` - Backend deployment
- `infrastructure/kubernetes/celery-worker.yaml` - Celery workers

### Особенности

- **Horizontal Pod Autoscaler (HPA)**:
  - Backend: 3-10 реплик (CPU: 70%, Memory: 80%)
  - Celery Worker: 2-5 реплик (CPU: 70%)
  
- **Health Checks**:
  - Liveness probe: `/health`
  - Readiness probe: `/health`
  
- **Resource Management**:
  - Requests: CPU 1, Memory 2Gi
  - Limits: CPU 2, Memory 4Gi

### Запуск

```bash
# Применение манифестов
kubectl apply -f infrastructure/kubernetes/deployment.yaml
kubectl apply -f infrastructure/kubernetes/celery-worker.yaml

# Проверка статуса
kubectl get deployments
kubectl get hpa

# Масштабирование вручную
kubectl scale deployment arin-backend --replicas=5
```

## Load Balancer (Nginx)

### Конфигурация

**Файл**: `infrastructure/nginx/nginx.conf`

Особенности:
- **Load Balancing Method**: Least Connections
- **Rate Limiting**: 100 req/s per IP
- **Connection Limiting**: 10 connections per IP
- **Gzip Compression**: Enabled
- **Health Check Endpoint**: `/health`

### Настройки

```nginx
upstream backend {
    least_conn;
    server backend:8000 max_fails=3 fail_timeout=30s;
}
```

## Load Testing

### Скрипты

1. **`backend/tests/load/load_test.py`** - Базовое нагрузочное тестирование
2. **`backend/tests/load/stress_test.py`** - Стресс-тестирование
3. **`backend/tests/load/bottleneck_analyzer.py`** - Анализ узких мест

### Запуск Load Test

```bash
cd backend/tests/load
python load_test.py
```

**Параметры**:
- Concurrent users: 100
- Requests per user: 10
- Total requests: 1000

**Метрики**:
- Success rate
- Requests per second
- Response times (mean, median, p95, p99)
- Status codes distribution

### Запуск Stress Test

```bash
python stress_test.py
```

**Тесты**:
1. **Gradual Load**: Постепенное увеличение нагрузки (10-500 users)
2. **Spike Load**: Резкий скачок нагрузки (1000 users)

**Результаты**:
- Maximum users handled
- Best throughput
- System degradation point

### Запуск Bottleneck Analyzer

```bash
python bottleneck_analyzer.py
```

**Анализ**:
- Медленные endpoints (>500ms)
- Критические узкие места (>1s)
- Endpoints с ошибками

## Целевые показатели

### Производительность

- ✅ Время ответа API < 500ms для стандартных запросов
- ✅ Система может обработать 1000+ запросов/минуту
- ✅ Кэширование снижает нагрузку на БД на 70%+

### Масштабируемость

- ✅ Система масштабируется горизонтально
- ✅ Выдерживает пиковые нагрузки
- ✅ Нет критических узких мест

## Мониторинг

### Метрики для отслеживания

1. **Request Rate**: Requests per second
2. **Response Time**: P50, P95, P99
3. **Error Rate**: Percentage of failed requests
4. **Resource Usage**: CPU, Memory, Network
5. **Queue Length**: Celery task queue length

### Инструменты

- Performance Monitor API: `/api/v1/performance/*`
- Kubernetes Metrics: `kubectl top pods`
- Docker Stats: `docker stats`

## Best Practices

1. **Начните с малого**: Тестируйте с небольшим количеством пользователей
2. **Постепенно увеличивайте**: Увеличивайте нагрузку постепенно
3. **Мониторьте метрики**: Отслеживайте все ключевые метрики
4. **Идентифицируйте узкие места**: Используйте bottleneck analyzer
5. **Оптимизируйте**: Устраняйте узкие места перед масштабированием
6. **Тестируйте регулярно**: Проводите load testing после изменений

## Troubleshooting

### Высокий response time

1. Проверьте индексы БД
2. Увеличьте кэширование
3. Оптимизируйте запросы
4. Масштабируйте backend

### Высокий error rate

1. Проверьте логи
2. Увеличьте ресурсы
3. Проверьте health checks
4. Масштабируйте сервисы

### Недостаточно ресурсов

1. Увеличьте resource limits
2. Масштабируйте горизонтально
3. Оптимизируйте использование ресурсов


# ARIN Platform - Deployment Guide

## Обзор

Руководство по развертыванию ARIN Platform в production окружении.

## Предварительные требования

### Инфраструктура

- **Серверы**: Минимум 2 CPU, 4GB RAM (рекомендуется 4 CPU, 8GB RAM)
- **База данных**: PostgreSQL 15+ с TimescaleDB extension
- **Кэш**: Redis 7+
- **Граф БД**: Neo4j 5+
- **Load Balancer**: Nginx или Traefik
- **Container Orchestration**: Docker Swarm или Kubernetes

### Программное обеспечение

- Docker 20.10+
- Docker Compose 2.0+ (для Docker Swarm)
- Kubernetes 1.24+ (опционально)
- Python 3.10+ (для локального развертывания)

## Варианты развертывания

### Вариант 1: Docker Compose (Development/Staging)

```bash
# 1. Клонирование
git clone https://github.com/MRsaa1/arin-platform.git
cd arin-platform

# 2. Настройка
cp .env.example .env
# Отредактируйте .env

# 3. Запуск
docker-compose up -d

# 4. Проверка
curl http://localhost:8000/health
```

### Вариант 2: Docker Swarm (Production)

```bash
# 1. Инициализация Swarm
docker swarm init

# 2. Создание secrets
echo "your-secret-key" | docker secret create secret_key -
echo "your-db-password" | docker secret create db_password -

# 3. Deploy stack
docker stack deploy -c docker-compose.prod.yml arin-platform

# 4. Масштабирование
docker service scale arin-platform_backend=3

# 5. Проверка
docker service ls
docker service ps arin-platform_backend
```

### Вариант 3: Kubernetes (Production)

```bash
# 1. Создание namespace
kubectl create namespace arin-platform

# 2. Создание secrets
kubectl create secret generic arin-secrets \
  --from-literal=database-url=postgresql://... \
  --from-literal=redis-url=redis://... \
  --from-literal=nvidia-api-key=... \
  -n arin-platform

# 3. Применение манифестов
kubectl apply -f infrastructure/kubernetes/deployment.yaml -n arin-platform
kubectl apply -f infrastructure/kubernetes/celery-worker.yaml -n arin-platform

# 4. Проверка
kubectl get pods -n arin-platform
kubectl get hpa -n arin-platform
```

## Настройка базы данных

### PostgreSQL + TimescaleDB

```sql
-- Создание БД
CREATE DATABASE arin_db;
CREATE DATABASE arin_ts;

-- Подключение к TimescaleDB
\c arin_ts
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Применение схемы audit logs
\i backend/compliance/audit_schema.sql
```

### Neo4j

```bash
# Запуск Neo4j
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5

# Проверка
curl http://localhost:7474
```

### Redis

```bash
# Запуск Redis
docker run -d \
  --name redis \
  -p 6379:6379 \
  redis:7-alpine

# Проверка
redis-cli ping
```

## Настройка Load Balancer

### Nginx

```bash
# Копирование конфигурации
cp infrastructure/nginx/nginx.conf /etc/nginx/nginx.conf

# Для production с SSL
cp infrastructure/nginx/nginx-ssl.conf /etc/nginx/nginx.conf

# Добавление SSL сертификатов
# Поместите cert.pem и key.pem в /etc/nginx/ssl/

# Перезапуск
nginx -t
systemctl reload nginx
```

## Настройка Celery

### Запуск Worker

```bash
# Development
celery -A backend.tasks.celery_app worker --loglevel=info

# Production
celery -A backend.tasks.celery_app worker \
  --loglevel=info \
  --concurrency=4 \
  --max-tasks-per-child=1000
```

### Запуск Beat Scheduler

```bash
celery -A backend.tasks.celery_app beat --loglevel=info
```

## Мониторинг

### Health Checks

Настройте health checks для:
- Backend API: `GET /health`
- Database: `pg_isready`
- Redis: `redis-cli ping`
- Neo4j: HTTP check на порт 7474

### Метрики

Используйте `/api/v1/performance/health` для мониторинга:
- Request rate
- Response times (p50, p95, p99)
- Error rate
- Agent performance

### Логирование

Настройте централизованное логирование:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Loki + Grafana
- Cloud logging (AWS CloudWatch, Google Cloud Logging)

## Безопасность

### TLS/SSL

1. Получите SSL сертификаты (Let's Encrypt, или ваш CA)
2. Настройте Nginx с SSL (см. `nginx-ssl.conf`)
3. Включите HTTP to HTTPS redirect
4. Настройте security headers

### Secrets Management

В production используйте:
- HashiCorp Vault
- AWS Secrets Manager
- Kubernetes Secrets

Не храните секреты в `.env` файлах!

### Firewall

Настройте firewall:
- Разрешите только необходимые порты
- Ограничьте доступ к БД только с backend серверов
- Используйте VPN для административного доступа

## Backup Strategy

### Автоматические бэкапы

Настроены через Celery:
- Ежедневные бэкапы в 2:00
- Хранение 30 дней
- Автоматическая очистка старых бэкапов

### Ручные бэкапы

```bash
# Создание бэкапа
POST /api/v1/compliance/backup
{
  "backup_type": "full",
  "include_data": true,
  "include_models": true
}
```

### Восстановление

```bash
# Список бэкапов
GET /api/v1/compliance/backup

# Восстановление
POST /api/v1/compliance/backup/{backup_id}/restore
```

## Масштабирование

### Горизонтальное масштабирование

**Docker Swarm**:
```bash
docker service scale arin-platform_backend=5
```

**Kubernetes**:
- HPA автоматически масштабирует на основе CPU/Memory
- Или вручную: `kubectl scale deployment arin-backend --replicas=5`

### Вертикальное масштабирование

Увеличьте ресурсы серверов:
- CPU: 2 → 4 cores
- Memory: 4GB → 8GB
- Disk: Увеличьте для БД и логов

## Обновление

### Zero-downtime Deployment

**Docker Swarm**:
```bash
docker service update --image arin-platform/backend:new-version arin-platform_backend
```

**Kubernetes**:
```bash
kubectl set image deployment/arin-backend backend=arin-platform/backend:new-version
kubectl rollout status deployment/arin-backend
```

### Откат

**Docker Swarm**:
```bash
docker service rollback arin-platform_backend
```

**Kubernetes**:
```bash
kubectl rollout undo deployment/arin-backend
```

## Troubleshooting

См. [Troubleshooting Guide](troubleshooting-guide.md)

## Checklist для Production

- [ ] Все секреты в secrets manager
- [ ] TLS/SSL настроен
- [ ] Firewall настроен
- [ ] Мониторинг настроен
- [ ] Бэкапы настроены
- [ ] Health checks настроены
- [ ] Load balancer настроен
- [ ] Auto-scaling настроен
- [ ] Логирование настроено
- [ ] Документация обновлена


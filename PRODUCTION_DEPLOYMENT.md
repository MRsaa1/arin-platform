# ARIN Platform - Production Deployment Guide

## 🚀 Production Deployment Checklist

### Pre-Deployment

#### 1. Environment Configuration

- [ ] Все секреты перемещены в secrets manager (HashiCorp Vault, AWS Secrets Manager)
- [ ] `.env` файл НЕ используется в production
- [ ] Все API ключи обновлены и проверены
- [ ] SECRET_KEY изменен на уникальный и безопасный
- [ ] Database passwords изменены на сильные пароли
- [ ] CORS настроен для конкретных доменов (не `*`)

#### 2. Database Setup

- [ ] PostgreSQL + TimescaleDB установлены и настроены
- [ ] Созданы все необходимые БД
- [ ] Применены миграции
- [ ] Созданы индексы (см. `backend/database/indexes.py`)
- [ ] Применена схема audit logs (см. `backend/compliance/audit_schema.sql`)
- [ ] Настроены retention policies для TimescaleDB
- [ ] Настроены бэкапы БД

#### 3. Infrastructure

- [ ] Docker Swarm или Kubernetes кластер настроен
- [ ] Load balancer (Nginx/Traefik) настроен
- [ ] SSL/TLS сертификаты получены и настроены
- [ ] Firewall настроен (только необходимые порты)
- [ ] Monitoring система настроена (Prometheus, Grafana, etc.)
- [ ] Logging система настроена (ELK, Loki, etc.)

#### 4. Security

- [ ] TLS/SSL включен для всех соединений
- [ ] Security headers настроены (HSTS, X-Frame-Options, etc.)
- [ ] Rate limiting настроен
- [ ] API keys ротированы
- [ ] JWT secret key изменен
- [ ] RBAC роли назначены пользователям
- [ ] Audit logging включен

#### 5. Performance

- [ ] Connection pooling настроен
- [ ] Redis caching настроен
- [ ] Celery workers запущены
- [ ] Celery beat scheduler запущен
- [ ] Load testing проведен
- [ ] Performance baseline установлен

#### 6. Monitoring & Alerts

- [ ] Health checks настроены
- [ ] Performance metrics собираются
- [ ] Error tracking настроен (Sentry, etc.)
- [ ] Alerts настроены для критических событий
- [ ] Dashboard настроен (Grafana, etc.)

## 📦 Deployment Steps

### Step 1: Prepare Environment

```bash
# 1. Создайте production .env файл (НЕ коммитьте!)
cp .env.example .env.production

# 2. Заполните все секреты
# Используйте secrets manager в production!

# 3. Проверьте конфигурацию
python -c "from backend.config import settings; print('Config OK')"
```

### Step 2: Database Migration

```bash
# 1. Подключитесь к БД
psql -h <db_host> -U arin_user -d arin_db

# 2. Примените миграции (если есть)
# alembic upgrade head

# 3. Создайте индексы
\i backend/database/indexes.py

# 4. Примените audit schema
\i backend/compliance/audit_schema.sql
```

### Step 3: Build and Deploy

#### Docker Swarm

```bash
# 1. Build images
docker build -t arin-platform/backend:latest -f infrastructure/docker/Dockerfile.backend .

# 2. Tag for registry
docker tag arin-platform/backend:latest <registry>/arin-platform/backend:latest

# 3. Push to registry
docker push <registry>/arin-platform/backend:latest

# 4. Deploy stack
docker stack deploy -c docker-compose.prod.yml arin-platform

# 5. Проверка
docker service ls
docker service ps arin-platform_backend
```

#### Kubernetes

```bash
# 1. Создайте namespace
kubectl create namespace arin-platform

# 2. Создайте secrets
kubectl create secret generic arin-secrets \
  --from-literal=database-url=<db_url> \
  --from-literal=redis-url=<redis_url> \
  --from-literal=nvidia-api-key=<key> \
  --from-literal=openai-api-key=<key> \
  --from-literal=secret-key=<secret> \
  -n arin-platform

# 3. Примените манифесты
kubectl apply -f infrastructure/kubernetes/deployment.yaml -n arin-platform
kubectl apply -f infrastructure/kubernetes/celery-worker.yaml -n arin-platform

# 4. Проверка
kubectl get pods -n arin-platform
kubectl get services -n arin-platform
kubectl get hpa -n arin-platform
```

### Step 4: Post-Deployment Verification

```bash
# 1. Health check
curl https://api.arin-platform.com/health

# 2. API доступность
curl https://api.arin-platform.com/api/v1/agents

# 3. Проверка метрик
curl https://api.arin-platform.com/api/v1/performance/health

# 4. Проверка логов
docker logs arin-backend --tail 100
# или
kubectl logs -n arin-platform deployment/arin-backend --tail 100
```

## 🔧 Production Configuration

### Environment Variables

**Обязательные**:
```bash
# Database
DATABASE_URL=postgresql://user:password@db:5432/arin
TIMESCALEDB_URL=postgresql://user:password@timescaledb:5433/arin_ts
REDIS_URL=redis://redis:6379/0
NEO4J_URL=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=<strong_password>

# Security
SECRET_KEY=<generate_strong_random_key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Keys
NVIDIA_API_KEY=<your_key>
OPENAI_API_KEY=<your_key>

# Logging
LOG_LEVEL=INFO  # или WARNING для production
```

**Опциональные**:
```bash
# External Integrations
RISK_ANALYZER_URL=https://risk-analyzer.example.com
NEWS_ANALYTICS_URL=https://news.example.com
INVESTMENT_DASHBOARD_URL=https://dashboard.example.com
CRYPTO_ANALYTICS_URL=https://crypto.example.com

# Secrets Management
SECRETS_BACKEND=vault  # или aws, local
VAULT_ADDR=http://vault:8200
VAULT_TOKEN=<vault_token>
```

### Nginx Configuration

Используйте `infrastructure/nginx/nginx-ssl.conf` для production:

1. Замените SSL сертификаты:
   ```bash
   # Поместите сертификаты в /etc/nginx/ssl/
   cert.pem
   key.pem
   ```

2. Настройте домены:
   ```nginx
   server_name api.arin-platform.com;
   ```

3. Настройте rate limiting под ваши нужды

### Database Configuration

**PostgreSQL**:
```sql
-- Увеличьте connection limits
ALTER SYSTEM SET max_connections = 200;
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET effective_cache_size = '12GB';

-- Перезапустите PostgreSQL
```

**TimescaleDB**:
```sql
-- Настройте retention policy
SELECT add_retention_policy('audit_logs', INTERVAL '3 years');
```

### Monitoring Setup

#### Prometheus Metrics

Добавьте Prometheus endpoint (опционально):
```python
from prometheus_fastapi_instrumentator import Instrumentator

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)
```

#### Health Checks

Настройте health checks для:
- Kubernetes: liveness/readiness probes
- Docker Swarm: healthcheck в docker-compose
- Load balancer: health endpoint

## 🔒 Security Hardening

### 1. Secrets Management

**НЕ используйте .env файлы в production!**

Используйте:
- HashiCorp Vault
- AWS Secrets Manager
- Kubernetes Secrets
- Docker Secrets

### 2. Network Security

- Используйте private networks для БД
- Ограничьте доступ к БД только с backend серверов
- Используйте VPN для административного доступа
- Настройте firewall правила

### 3. Application Security

- Включите HTTPS только
- Настройте security headers
- Включите rate limiting
- Регулярно обновляйте зависимости
- Мониторьте подозрительную активность

### 4. Data Security

- Шифрование at rest (БД)
- Шифрование in transit (TLS)
- Регулярные бэкапы
- Тестирование восстановления

## 📊 Monitoring & Alerts

### Key Metrics to Monitor

1. **Application Metrics**:
   - Request rate (RPS)
   - Response times (p50, p95, p99)
   - Error rate
   - Health score

2. **Infrastructure Metrics**:
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network traffic

3. **Database Metrics**:
   - Connection pool usage
   - Query performance
   - Replication lag

4. **Business Metrics**:
   - Active agents
   - Risk analyses per day
   - API key usage
   - User activity

### Alert Rules

Настройте alerts для:
- Health score < 0.7
- Error rate > 5%
- Response time p95 > 1s
- CPU usage > 80%
- Memory usage > 90%
- Database connections > 80%
- Disk usage > 85%

## 🔄 Maintenance

### Regular Tasks

1. **Ежедневно**:
   - Проверка health checks
   - Проверка критических алертов
   - Мониторинг метрик

2. **Еженедельно**:
   - Проверка логов на ошибки
   - Анализ производительности
   - Проверка бэкапов

3. **Ежемесячно**:
   - Обновление зависимостей
   - Security audit
   - Performance review
   - Capacity planning

### Backup Strategy

1. **Database**: Ежедневные автоматические бэкапы
2. **ML Models**: После каждого переобучения
3. **Configuration**: При каждом изменении
4. **Retention**: 30 дней для бэкапов

### Update Procedure

1. Создайте бэкап
2. Протестируйте обновление на staging
3. Разверните на production (zero-downtime)
4. Проверьте health checks
5. Мониторьте метрики
6. Откатите при проблемах

## ✅ Final Verification

Перед объявлением production-ready:

- [ ] Все health checks проходят
- [ ] Load testing пройден успешно
- [ ] Security audit проведен
- [ ] Backup и recovery протестированы
- [ ] Monitoring настроен и работает
- [ ] Alerts настроены и тестированы
- [ ] Документация актуальна
- [ ] Team обучена
- [ ] Support процесс настроен

## 🆘 Rollback Procedure

В случае проблем:

**Docker Swarm**:
```bash
docker service rollback arin-platform_backend
```

**Kubernetes**:
```bash
kubectl rollout undo deployment/arin-backend -n arin-platform
```

**Manual**:
```bash
# Восстановите из бэкапа
POST /api/v1/compliance/backup/{backup_id}/restore
```

## 📞 Support

- **Production Issues**: production-support@arin-platform.com
- **Emergency**: emergency@arin-platform.com
- **Documentation**: https://github.com/MRsaa1/arin-platform

---

**Готово к production deployment!** 🚀


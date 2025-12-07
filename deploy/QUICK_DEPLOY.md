# ⚡ Быстрое развертывание ARIN Platform

## Статус развертывания

✅ **Проект развернут на**: https://arin.saa-alliance.com

## Важные замечания

### ⚠️ КРИТИЧНО: Настройте API ключи!

Отредактируйте `.env` на сервере и добавьте ваши API ключи:

```bash
ssh root@104.248.70.69
nano /opt/arin-platform/.env
```

Замените:
- `NVIDIA_API_KEY=your-nvidia-api-key` → ваш реальный ключ
- `OPENAI_API_KEY=your-openai-api-key` → ваш реальный ключ (опционально)

### Изолированные порты

Все сервисы используют изолированные порты, привязанные только к localhost:
- PostgreSQL: `127.0.0.1:15432`
- TimescaleDB: `127.0.0.1:15433`
- Neo4j: `127.0.0.1:17687` и `127.0.0.1:17474`
- Redis: `127.0.0.1:16379`
- Backend: `127.0.0.1:18000`
- Frontend: `127.0.0.1:3000`

**Нет конфликтов с другими проектами!** ✅

## Управление сервисами

### Backend (Docker)
```bash
# Статус
docker-compose -f /opt/arin-platform/deploy/docker-compose.prod-server.yml ps

# Логи
docker-compose -f /opt/arin-platform/deploy/docker-compose.prod-server.yml logs -f backend

# Перезапуск
docker-compose -f /opt/arin-platform/deploy/docker-compose.prod-server.yml restart backend
```

### Frontend (PM2)
```bash
# Статус
pm2 status

# Логи
pm2 logs arin-frontend

# Перезапуск
pm2 restart arin-frontend
```

### Nginx
```bash
# Статус
systemctl status nginx

# Перезапуск
systemctl reload nginx

# Логи
tail -f /var/log/nginx/arin-access.log
tail -f /var/log/nginx/arin-error.log
```

## Обновление проекта

```bash
ssh root@104.248.70.69

# Обновление кода
cd /opt/arin-platform
git pull origin main

# Пересборка backend
docker-compose -f deploy/docker-compose.prod-server.yml down
docker-compose -f deploy/docker-compose.prod-server.yml build
docker-compose -f deploy/docker-compose.prod-server.yml up -d

# Обновление frontend
cd frontend
npm install
npm run build
pm2 restart arin-frontend
```

## Проверка работоспособности

```bash
# Health check
curl https://arin.saa-alliance.com/health

# API
curl https://arin.saa-alliance.com/api/v1/agents

# Frontend
curl https://arin.saa-alliance.com/
```

## Мониторинг ресурсов

```bash
# Использование памяти
free -h

# Использование диска
df -h

# Docker контейнеры
docker stats

# PM2 процессы
pm2 monit
```

---

**Проект готов к использованию!** 🚀


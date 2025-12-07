# 🚀 ARIN Platform - Production Deployment Guide

## Сервер
- **IP**: 104.248.70.69
- **Домен**: arin.saa-alliance.com
- **ОС**: Ubuntu 24.04 LTS
- **Ресурсы**: 4 vCPU, 8GB RAM, 240GB Disk

## ⚠️ КРИТИЧНО: Изоляция от других проектов

Все порты изолированы и привязаны только к localhost (127.0.0.1):
- PostgreSQL: `127.0.0.1:15432` (вместо стандартного 5432)
- TimescaleDB: `127.0.0.1:15433` (вместо стандартного 5433)
- Neo4j: `127.0.0.1:17687` и `127.0.0.1:17474`
- Redis: `127.0.0.1:16379` (вместо стандартного 6379)
- Backend API: `127.0.0.1:18000` (вместо стандартного 8000)
- Frontend: `127.0.0.1:3000` (стандартный, но через Nginx)

**Доступ к сервисам только через Nginx на портах 80/443**

## Шаг 1: Подключение к серверу

```bash
ssh root@104.248.70.69
```

## Шаг 2: Установка зависимостей

```bash
# Обновление системы
apt-get update && apt-get upgrade -y

# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh
systemctl enable docker
systemctl start docker

# Установка Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Установка Nginx и Certbot
apt-get install -y nginx certbot python3-certbot-nginx
```

## Шаг 3: Клонирование проекта

```bash
# Создание директории
mkdir -p /opt/arin-platform
cd /opt

# Клонирование репозитория
git clone https://github.com/MRsaa1/arin-platform.git arin-platform
cd arin-platform
```

## Шаг 4: Настройка переменных окружения

```bash
# Создание .env из примера
cp .env.example .env
nano .env
```

**ВАЖНО**: Заполните все секреты:
- `POSTGRES_PASSWORD` - сильный пароль
- `TIMESCALEDB_PASSWORD` - сильный пароль
- `NEO4J_PASSWORD` - сильный пароль
- `NVIDIA_API_KEY` - ваш NVIDIA API ключ
- `OPENAI_API_KEY` - ваш OpenAI API ключ (опционально)
- `SECRET_KEY` - сгенерируйте: `openssl rand -hex 32`

## Шаг 5: Настройка Nginx

```bash
# Копирование конфигурации
cp deploy/nginx-arin.conf /etc/nginx/sites-available/arin.saa-alliance.com

# Создание символической ссылки
ln -s /etc/nginx/sites-available/arin.saa-alliance.com /etc/nginx/sites-enabled/arin.saa-alliance.com

# Удаление дефолтной конфигурации (если нужно)
rm -f /etc/nginx/sites-enabled/default

# Проверка конфигурации
nginx -t
```

## Шаг 6: Получение SSL сертификата

```bash
# Получение сертификата Let's Encrypt
certbot --nginx -d arin.saa-alliance.com

# Автоматическое обновление
certbot renew --dry-run
```

## Шаг 7: Запуск Backend

```bash
cd /opt/arin-platform

# Использование production конфигурации
docker-compose -f deploy/docker-compose.prod-server.yml build
docker-compose -f deploy/docker-compose.prod-server.yml up -d

# Проверка статуса
docker-compose -f deploy/docker-compose.prod-server.yml ps

# Логи
docker-compose -f deploy/docker-compose.prod-server.yml logs -f backend
```

## Шаг 8: Настройка Frontend

```bash
cd /opt/arin-platform/frontend

# Установка зависимостей
npm install

# Сборка production версии
npm run build

# Запуск в production режиме (через PM2 для надежности)
npm install -g pm2
pm2 start npm --name "arin-frontend" -- start
pm2 save
pm2 startup  # Настройка автозапуска
```

## Шаг 9: Перезапуск Nginx

```bash
# Перезапуск Nginx
systemctl restart nginx
systemctl status nginx
```

## Шаг 10: Проверка

```bash
# Health check
curl https://arin.saa-alliance.com/health

# API
curl https://arin.saa-alliance.com/api/v1/agents

# Frontend
curl https://arin.saa-alliance.com/
```

## Мониторинг

### Логи Backend
```bash
docker-compose -f deploy/docker-compose.prod-server.yml logs -f backend
```

### Логи Frontend
```bash
pm2 logs arin-frontend
```

### Логи Nginx
```bash
tail -f /var/log/nginx/arin-access.log
tail -f /var/log/nginx/arin-error.log
```

### Статус сервисов
```bash
# Docker контейнеры
docker-compose -f deploy/docker-compose.prod-server.yml ps

# PM2 процессы
pm2 status

# Nginx
systemctl status nginx
```

## Обновление проекта

```bash
cd /opt/arin-platform

# Обновление кода
git pull origin main

# Пересборка и перезапуск
docker-compose -f deploy/docker-compose.prod-server.yml down
docker-compose -f deploy/docker-compose.prod-server.yml build
docker-compose -f deploy/docker-compose.prod-server.yml up -d

# Обновление frontend
cd frontend
npm install
npm run build
pm2 restart arin-frontend
```

## Резервное копирование

```bash
# Бэкап БД
docker-compose -f deploy/docker-compose.prod-server.yml exec postgres pg_dump -U arin arin > /opt/backups/arin_$(date +%Y%m%d_%H%M%S).sql

# Автоматический бэкап (cron)
0 2 * * * docker-compose -f /opt/arin-platform/deploy/docker-compose.prod-server.yml exec -T postgres pg_dump -U arin arin > /opt/backups/arin_$(date +\%Y\%m\%d).sql
```

## Безопасность

- ✅ Все порты БД привязаны только к localhost
- ✅ SSL/TLS через Let's Encrypt
- ✅ Security headers настроены
- ✅ Изолированная Docker сеть
- ✅ Отдельные volumes для данных

## Troubleshooting

### Проблема с портами
```bash
# Проверка занятых портов
ss -tuln | grep -E ':(80|443|15432|15433|16379|17687|18000|3000)'
```

### Проблема с SSL
```bash
# Обновление сертификата
certbot renew
systemctl reload nginx
```

### Проблема с Docker
```bash
# Перезапуск Docker
systemctl restart docker
docker-compose -f deploy/docker-compose.prod-server.yml up -d
```

---

**Готово! Проект развернут на https://arin.saa-alliance.com** 🎉


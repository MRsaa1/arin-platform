#!/bin/bash
# ARIN Platform - Deployment Script for Production Server
# Сервер: 104.248.70.69
# Домен: arin.saa-alliance.com

set -e

SERVER_IP="104.248.70.69"
DOMAIN="arin.saa-alliance.com"
PROJECT_DIR="/opt/arin-platform"
SSH_USER="root"

echo "🚀 ARIN Platform - Production Deployment"
echo "========================================"
echo "Server: $SERVER_IP"
echo "Domain: $DOMAIN"
echo ""

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Проверка подключения
echo "📡 Проверка подключения к серверу..."
if ! ssh -o ConnectTimeout=5 $SSH_USER@$SERVER_IP "echo 'Connected'" > /dev/null 2>&1; then
    echo -e "${RED}❌ Не удалось подключиться к серверу${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Подключение установлено${NC}"
echo ""

# Проверка портов
echo "🔍 Проверка занятых портов..."
OCCUPIED_PORTS=$(ssh $SSH_USER@$SERVER_IP "ss -tuln | grep -E ':(80|443|8000|5432|5433|6379|7687|7474)' | awk '{print \$5}' | cut -d: -f2 | sort -u" 2>/dev/null || echo "")
if [ ! -z "$OCCUPIED_PORTS" ]; then
    echo -e "${YELLOW}⚠️  Занятые порты: $OCCUPIED_PORTS${NC}"
    echo "Используем изолированные порты для ARIN"
else
    echo -e "${GREEN}✅ Порты свободны${NC}"
fi
echo ""

# Создание директории проекта
echo "📁 Создание директории проекта..."
ssh $SSH_USER@$SERVER_IP "mkdir -p $PROJECT_DIR && chmod 755 $PROJECT_DIR"
echo -e "${GREEN}✅ Директория создана${NC}"
echo ""

# Клонирование/обновление репозитория
echo "📥 Клонирование репозитория..."
if ssh $SSH_USER@$SERVER_IP "[ -d $PROJECT_DIR/.git ]"; then
    echo "Обновление существующего репозитория..."
    ssh $SSH_USER@$SERVER_IP "cd $PROJECT_DIR && git pull origin main"
else
    echo "Клонирование нового репозитория..."
    ssh $SSH_USER@$SERVER_IP "cd /opt && git clone https://github.com/MRsaa1/arin-platform.git $PROJECT_DIR"
fi
echo -e "${GREEN}✅ Репозиторий готов${NC}"
echo ""

# Создание .env файла
echo "🔐 Настройка переменных окружения..."
if ! ssh $SSH_USER@$SERVER_IP "[ -f $PROJECT_DIR/.env ]"; then
    echo "Создание .env из .env.example..."
    ssh $SSH_USER@$SERVER_IP "cd $PROJECT_DIR && cp .env.example .env"
    echo -e "${YELLOW}⚠️  ВАЖНО: Отредактируйте .env на сервере и добавьте все секреты!${NC}"
    echo "   ssh $SSH_USER@$SERVER_IP"
    echo "   nano $PROJECT_DIR/.env"
else
    echo -e "${GREEN}✅ .env файл уже существует${NC}"
fi
echo ""

# Установка Docker (если не установлен)
echo "🐳 Проверка Docker..."
if ! ssh $SSH_USER@$SERVER_IP "command -v docker > /dev/null 2>&1"; then
    echo "Установка Docker..."
    ssh $SSH_USER@$SERVER_IP "curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh && rm get-docker.sh"
    ssh $SSH_USER@$SERVER_IP "systemctl enable docker && systemctl start docker"
else
    echo -e "${GREEN}✅ Docker установлен${NC}"
fi
echo ""

# Установка Docker Compose (если не установлен)
if ! ssh $SSH_USER@$SERVER_IP "command -v docker-compose > /dev/null 2>&1"; then
    echo "Установка Docker Compose..."
    ssh $SSH_USER@$SERVER_IP "curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose"
else
    echo -e "${GREEN}✅ Docker Compose установлен${NC}"
fi
echo ""

# Настройка изолированных портов
echo "🔧 Настройка изолированных портов..."
cat > /tmp/arin-docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: arin-postgres
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-arin}
      POSTGRES_USER: ${POSTGRES_USER:-arin}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - arin_postgres_data:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:15432:5432"  # Изолированный порт
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-arin}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - arin-network

  timescaledb:
    image: timescale/timescaledb:latest-pg15
    container_name: arin-timescaledb
    environment:
      POSTGRES_DB: ${TIMESCALEDB_DB:-arin_ts}
      POSTGRES_USER: ${TIMESCALEDB_USER:-arin}
      POSTGRES_PASSWORD: ${TIMESCALEDB_PASSWORD}
    volumes:
      - arin_timescaledb_data:/var/lib/postgresql/data
    ports:
      - "127.0.0.1:15433:5432"  # Изолированный порт
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${TIMESCALEDB_USER:-arin}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - arin-network

  neo4j:
    image: neo4j:5
    container_name: arin-neo4j
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
      NEO4J_PLUGINS: '["apoc"]'
    volumes:
      - arin_neo4j_data:/data
      - arin_neo4j_logs:/logs
    ports:
      - "127.0.0.1:17687:7687"  # Изолированный порт
      - "127.0.0.1:17474:7474"  # Изолированный порт
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "${NEO4J_PASSWORD}", "RETURN 1"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - arin-network

  redis:
    image: redis:7-alpine
    container_name: arin-redis
    volumes:
      - arin_redis_data:/data
    ports:
      - "127.0.0.1:16379:6379"  # Изолированный порт
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - arin-network

  backend:
    build:
      context: .
      dockerfile: infrastructure/docker/Dockerfile.backend
    container_name: arin-backend
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-arin}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-arin}
      TIMESCALEDB_URL: postgresql://${TIMESCALEDB_USER:-arin}:${TIMESCALEDB_PASSWORD}@timescaledb:5432/${TIMESCALEDB_DB:-arin_ts}
      REDIS_URL: redis://redis:6379
      NEO4J_URL: bolt://neo4j:7687
      NEO4J_USER: neo4j
      NEO4J_PASSWORD: ${NEO4J_PASSWORD}
      NVIDIA_API_KEY: ${NVIDIA_API_KEY}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      SECRET_KEY: ${SECRET_KEY}
    ports:
      - "127.0.0.1:18000:8000"  # Изолированный порт (только localhost)
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      neo4j:
        condition: service_healthy
    volumes:
      - ./backend:/app/backend
    networks:
      - arin-network
    restart: unless-stopped

volumes:
  arin_postgres_data:
  arin_timescaledb_data:
  arin_neo4j_data:
  arin_neo4j_logs:
  arin_redis_data:

networks:
  arin-network:
    driver: bridge
    name: arin-network
EOF

scp /tmp/arin-docker-compose.yml $SSH_USER@$SERVER_IP:$PROJECT_DIR/docker-compose.prod.yml
echo -e "${GREEN}✅ Конфигурация портов создана${NC}"
echo ""

# Настройка Nginx
echo "🌐 Настройка Nginx..."
ssh $SSH_USER@$SERVER_IP "apt-get update && apt-get install -y nginx certbot python3-certbot-nginx" 2>/dev/null || true

cat > /tmp/arin-nginx.conf << 'EOF'
server {
    listen 80;
    listen [::]:80;
    server_name arin.saa-alliance.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name arin.saa-alliance.com;

    # SSL certificates (will be set up by certbot)
    ssl_certificate /etc/letsencrypt/live/arin.saa-alliance.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/arin.saa-alliance.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Logging
    access_log /var/log/nginx/arin-access.log;
    error_log /var/log/nginx/arin-error.log;

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:18000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Frontend (Next.js)
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check
    location /health {
        proxy_pass http://127.0.0.1:18000/health;
        access_log off;
    }
}
EOF

scp /tmp/arin-nginx.conf $SSH_USER@$SERVER_IP:/etc/nginx/sites-available/arin.saa-alliance.com
ssh $SSH_USER@$SERVER_IP "ln -sf /etc/nginx/sites-available/arin.saa-alliance.com /etc/nginx/sites-enabled/arin.saa-alliance.com"
echo -e "${GREEN}✅ Nginx настроен${NC}"
echo ""

# Проверка Nginx конфигурации
echo "🔍 Проверка Nginx конфигурации..."
ssh $SSH_USER@$SERVER_IP "nginx -t" || echo -e "${YELLOW}⚠️  Nginx конфигурация требует SSL сертификатов${NC}"
echo ""

echo "✅ Базовая настройка завершена!"
echo ""
echo "Следующие шаги:"
echo "1. Отредактируйте .env на сервере:"
echo "   ssh $SSH_USER@$SERVER_IP"
echo "   nano $PROJECT_DIR/.env"
echo ""
echo "2. Получите SSL сертификат:"
echo "   certbot --nginx -d arin.saa-alliance.com"
echo ""
echo "3. Запустите проект:"
echo "   cd $PROJECT_DIR"
echo "   docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "4. Запустите frontend (в отдельном процессе):"
echo "   cd $PROJECT_DIR/frontend"
echo "   npm install"
echo "   npm run build"
echo "   npm start"


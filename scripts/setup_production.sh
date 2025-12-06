#!/bin/bash

# ARIN Platform - Production Setup Script
# Автоматическая настройка production окружения

set -e

echo "🚀 ARIN Platform - Production Setup"
echo "===================================="
echo ""

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Проверка предварительных требований
echo "📋 Проверка предварительных требований..."

command -v docker >/dev/null 2>&1 || { echo -e "${RED}❌ Docker не установлен${NC}"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo -e "${RED}❌ Docker Compose не установлен${NC}"; exit 1; }
command -v psql >/dev/null 2>&1 || { echo -e "${YELLOW}⚠️  PostgreSQL client не установлен (опционально)${NC}"; }

echo -e "${GREEN}✅ Предварительные требования выполнены${NC}"
echo ""

# Создание .env.production
if [ ! -f ".env.production" ]; then
    echo "📝 Создание .env.production..."
    cp .env.example .env.production
    echo -e "${YELLOW}⚠️  ВАЖНО: Отредактируйте .env.production и добавьте все секреты!${NC}"
    echo ""
else
    echo -e "${GREEN}✅ .env.production уже существует${NC}"
fi

# Проверка секретов
echo "🔒 Проверка секретов..."
if grep -q "your-" .env.production 2>/dev/null; then
    echo -e "${RED}❌ В .env.production есть placeholder значения!${NC}"
    echo "   Замените все 'your-*' значения на реальные"
    exit 1
fi
echo -e "${GREEN}✅ Секреты настроены${NC}"
echo ""

# Создание директорий
echo "📁 Создание необходимых директорий..."
mkdir -p backups
mkdir -p logs
mkdir -p backend/models
mkdir -p infrastructure/nginx/ssl
echo -e "${GREEN}✅ Директории созданы${NC}"
echo ""

# Генерация SECRET_KEY если нужно
if grep -q "change-this-secret-key" .env.production 2>/dev/null; then
    echo "🔑 Генерация SECRET_KEY..."
    SECRET_KEY=$(openssl rand -hex 32)
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env.production
    else
        # Linux
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env.production
    fi
    echo -e "${GREEN}✅ SECRET_KEY сгенерирован${NC}"
    echo ""
fi

# Проверка SSL сертификатов
echo "🔐 Проверка SSL сертификатов..."
if [ ! -f "infrastructure/nginx/ssl/cert.pem" ] || [ ! -f "infrastructure/nginx/ssl/key.pem" ]; then
    echo -e "${YELLOW}⚠️  SSL сертификаты не найдены${NC}"
    echo "   Для production добавьте сертификаты в infrastructure/nginx/ssl/"
    echo "   Или используйте Let's Encrypt"
else
    echo -e "${GREEN}✅ SSL сертификаты найдены${NC}"
fi
echo ""

# Проверка Docker
echo "🐳 Проверка Docker..."
if docker ps >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker работает${NC}"
else
    echo -e "${RED}❌ Docker не запущен${NC}"
    exit 1
fi
echo ""

# Финальная проверка
echo "✅ Production setup завершен!"
echo ""
echo "Следующие шаги:"
echo "1. Проверьте .env.production - все секреты должны быть заполнены"
echo "2. Добавьте SSL сертификаты в infrastructure/nginx/ssl/"
echo "3. Настройте БД и примените миграции"
echo "4. Запустите: docker-compose -f docker-compose.prod.yml up -d"
echo "5. Проверьте: curl http://localhost/health"
echo ""
echo "Для детальной информации см. PRODUCTION_DEPLOYMENT.md"


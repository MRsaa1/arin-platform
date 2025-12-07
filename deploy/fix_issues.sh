#!/bin/bash
# ARIN Platform - Fix Common Issues Script

cd /opt/arin-platform

echo "🔧 Исправление проблем ARIN Platform..."

# Экспорт переменных из .env
export $(grep -v '^#' .env | grep -v '^$' | xargs)

# 1. Перезапуск backend без зависимости от Neo4j
echo "📦 Перезапуск backend..."
docker-compose -f deploy/docker-compose.prod-server.yml up -d backend --no-deps

# 2. Перезапуск frontend в PM2
echo "🌐 Перезапуск frontend..."
cd frontend
pm2 delete arin-frontend 2>/dev/null
pm2 start npm --name "arin-frontend" -- start
pm2 save

# 3. Проверка статуса
echo ""
echo "✅ Проверка статуса..."
cd /opt/arin-platform
docker-compose -f deploy/docker-compose.prod-server.yml ps

echo ""
echo "📊 PM2 статус:"
pm2 status | grep arin

echo ""
echo "🏥 Health Check:"
curl -s http://127.0.0.1:18000/health 2>&1 | head -5

echo ""
echo "✅ Готово!"


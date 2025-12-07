#!/bin/bash
# ARIN Platform - Start Script
# Автоматически экспортирует переменные окружения и запускает сервисы

cd /opt/arin-platform

# Экспорт переменных из .env
export $(grep -v '^#' .env | grep -v '^$' | xargs)

# Запуск сервисов
docker-compose -f deploy/docker-compose.prod-server.yml up -d

echo "✅ ARIN Platform services started"
echo "Backend: http://127.0.0.1:18000"
echo "Frontend: http://127.0.0.1:3000"


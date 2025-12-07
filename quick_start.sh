#!/bin/bash
# Quick start script for ARIN Platform

echo "🚀 ARIN Platform - Quick Start"
echo "=============================="
echo ""

# Проверка директории
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Ошибка: docker-compose.yml не найден"
    echo "Убедитесь, что вы в директории проекта:"
    echo "  cd ~/arin-platform"
    echo "  или"
    echo "  cd /Users/artur220513timur110415gmail.com/arin-platform"
    exit 1
fi

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен"
    echo "Установите Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo "❌ Docker не запущен"
    echo "Запустите Docker Desktop и попробуйте снова"
    exit 1
fi

echo "✅ Docker работает"
echo ""

# Проверка .env
if [ ! -f ".env" ]; then
    echo "⚠️  .env файл не найден, создаю из .env.example..."
    cp .env.example .env
    echo "⚠️  ВАЖНО: Отредактируйте .env и установите пароли!"
fi

echo "🚀 Запуск контейнеров..."
docker-compose up -d

echo ""
echo "⏳ Ожидание запуска сервисов..."
sleep 5

echo ""
echo "✅ Проект запущен!"
echo ""
echo "📊 Проверка статуса:"
docker-compose ps

echo ""
echo "🌐 Доступные endpoints:"
echo "  - API: http://localhost:8000"
echo "  - Docs: http://localhost:8000/docs"
echo "  - Health: http://localhost:8000/health"
echo ""
echo "📋 Полезные команды:"
echo "  - Логи: docker-compose logs -f backend"
echo "  - Остановка: docker-compose down"
echo "  - Перезапуск: docker-compose restart"

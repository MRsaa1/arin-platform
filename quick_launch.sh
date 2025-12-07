#!/bin/bash
# Быстрый запуск ARIN Platform

echo "🚀 ARIN Platform - Quick Launch"
echo "================================"
echo ""

# Переход в директорию проекта
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📁 Директория: $(pwd)"
echo ""

# Проверка файлов
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml не найден!"
    echo "Убедитесь, что вы в директории проекта"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "⚠️  .env файл не найден, создаю из .env.example..."
    cp .env.example .env
    echo "✅ .env создан. Отредактируйте его перед production!"
fi

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    echo "Установите Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo "❌ Docker не запущен!"
    echo "Запустите Docker Desktop"
    exit 1
fi

echo "✅ Docker работает"
echo ""

# Запуск
echo "🚀 Запуск сервисов..."
docker-compose up -d

echo ""
echo "⏳ Ожидание запуска сервисов..."
sleep 5

# Проверка статуса
echo ""
echo "📊 Статус сервисов:"
docker-compose ps

echo ""
echo "✅ Проект запущен!"
echo ""
echo "📊 API: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo "❤️  Health: http://localhost:8000/health"
echo ""
echo "Логи: docker-compose logs -f backend"
echo "Остановка: docker-compose down"

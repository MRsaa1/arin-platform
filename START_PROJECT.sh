#!/bin/bash
echo "🚀 ARIN Platform - Quick Start"
echo "=============================="
echo ""

# Проверка Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker найден"
    if docker ps &> /dev/null; then
        echo "✅ Docker работает"
        echo ""
        echo "Запуск через Docker..."
        docker-compose up -d
        echo ""
        echo "✅ Сервисы запущены!"
        echo "📊 API: http://localhost:8000"
        echo "📚 Docs: http://localhost:8000/docs"
        echo "❤️  Health: http://localhost:8000/health"
        echo ""
        echo "Логи: docker-compose logs -f backend"
    else
        echo "❌ Docker не запущен. Запустите Docker Desktop"
        exit 1
    fi
else
    echo "❌ Docker не установлен"
    echo ""
    echo "Установите Docker Desktop:"
    echo "https://www.docker.com/products/docker-desktop"
    echo ""
    echo "Или запустите локально (см. QUICK_START.md)"
    exit 1
fi

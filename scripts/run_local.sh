#!/bin/bash
# ARIN Platform - Local Run Script (без Docker)

echo "🚀 ARIN Platform - Локальный запуск"
echo "===================================="
echo ""

cd "$(dirname "$0")/.."

# Проверка .env
if [ ! -f .env ]; then
    echo "❌ .env файл не найден"
    echo "Создайте .env из .env.example"
    exit 1
fi

# Загрузка переменных окружения
export $(cat .env | grep -v '^#' | xargs)

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден"
    exit 1
fi

echo "✅ Python найден: $(python3 --version)"
echo ""

# Проверка зависимостей
echo "📦 Проверка зависимостей..."
cd backend

if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  FastAPI не установлен. Устанавливаю..."
    pip3 install -r requirements.txt
fi

echo "✅ Зависимости готовы"
echo ""

# Запуск
echo "🚀 Запуск backend сервера..."
echo "📊 API будет доступен на: http://localhost:8000"
echo "📚 Документация: http://localhost:8000/docs"
echo "❤️  Health check: http://localhost:8000/health"
echo ""
echo "⚠️  ВАЖНО: Убедитесь, что PostgreSQL, Redis и Neo4j запущены!"
echo ""

python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload


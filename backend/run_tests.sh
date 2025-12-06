#!/bin/bash

# Скрипт для запуска тестов ARIN Platform

set -e

echo "🧪 ARIN Platform - Запуск тестов"
echo "================================"

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Проверка установки pytest
if ! command -v pytest &> /dev/null; then
    echo "❌ pytest не установлен. Установите: pip install pytest pytest-asyncio pytest-cov"
    exit 1
fi

# Параметры по умолчанию
TEST_TYPE="${1:-all}"
COVERAGE="${2:-false}"

case $TEST_TYPE in
    unit)
        echo -e "${GREEN}📦 Запуск Unit тестов...${NC}"
        pytest tests/unit -m unit -v
        ;;
    integration)
        echo -e "${GREEN}🔗 Запуск Integration тестов...${NC}"
        pytest tests/integration -m integration -v
        ;;
    e2e)
        echo -e "${GREEN}🔄 Запуск E2E тестов...${NC}"
        pytest tests/e2e -m e2e -v
        ;;
    load)
        echo -e "${YELLOW}⚡ Запуск тестов нагрузки...${NC}"
        pytest tests/test_load.py -m slow -v
        ;;
    all)
        echo -e "${GREEN}🚀 Запуск всех тестов...${NC}"
        if [ "$COVERAGE" = "true" ]; then
            pytest --cov=backend --cov-report=term-missing --cov-report=html -v
            echo -e "${GREEN}✅ Отчет о покрытии создан в htmlcov/index.html${NC}"
        else
            pytest -v
        fi
        ;;
    *)
        echo "Использование: ./run_tests.sh [unit|integration|e2e|load|all] [coverage]"
        echo "Примеры:"
        echo "  ./run_tests.sh unit"
        echo "  ./run_tests.sh all true"
        exit 1
        ;;
esac

echo -e "${GREEN}✅ Тесты завершены${NC}"


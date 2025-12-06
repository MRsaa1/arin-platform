#!/bin/bash

# Скрипт для безопасной публикации ARIN Platform на GitHub
# Использование: ./deploy_to_github.sh

set -e  # Остановка при ошибке

echo "🚀 ARIN Platform - GitHub Deployment Script"
echo "============================================"
echo ""

# Проверка что мы в правильной директории
if [ ! -f "README.md" ] || [ ! -d "backend" ]; then
    echo "❌ Ошибка: Запустите скрипт из корневой директории arin-platform"
    exit 1
fi

# Проверка безопасности
echo "🔒 Проверка безопасности..."
echo ""

# Проверка на .env файлы
if [ -f ".env" ]; then
    echo "⚠️  ВНИМАНИЕ: Найден .env файл"
    echo "   Убедитесь, что он в .gitignore (должен быть)"
    read -p "   Продолжить? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Проверка на реальные API ключи
echo "🔍 Проверка на наличие секретов в коде..."
if grep -r "sk-[a-zA-Z0-9]\{32,\}" . --exclude-dir=.git --exclude-dir=node_modules --exclude="*.json" 2>/dev/null; then
    echo "❌ ОШИБКА: Найдены потенциальные OpenAI API ключи!"
    exit 1
fi

if grep -r "nvapi-[a-zA-Z0-9]\{32,\}" . --exclude-dir=.git --exclude-dir=node_modules --exclude="*.json" 2>/dev/null; then
    echo "❌ ОШИБКА: Найдены потенциальные NVIDIA API ключи!"
    exit 1
fi

echo "✅ Проверка безопасности пройдена"
echo ""

# Инициализация Git (если еще не инициализирован)
if [ ! -d ".git" ]; then
    echo "📦 Инициализация Git репозитория..."
    git init
    echo "✅ Git инициализирован"
else
    echo "ℹ️  Git репозиторий уже инициализирован"
fi

# Добавление всех файлов
echo ""
echo "📝 Добавление файлов в staging..."
git add .
echo "✅ Файлы добавлены"

# Проверка что .env не включен
if git status --short | grep -q "\.env$"; then
    echo "❌ ОШИБКА: .env файл попал в staging!"
    echo "   Удалите его: git reset HEAD .env"
    exit 1
fi

# Создание коммита
echo ""
echo "💾 Создание коммита..."
git commit -m "Initial commit: ARIN Platform - Autonomous Risk Intelligence Network

- Multi-agent system for predictive risk management
- 6 specialized risk agents (Credit, Market, Operational, Liquidity, Regulatory, Systemic)
- Graph-based dependency analysis with GNN
- LLM integration (DeepSeek R1, GPT-4)
- ML models (XGBoost, GNN)
- Production-ready with Docker/Kubernetes support
- Performance optimization and load testing tools
- Complete documentation and security best practices" || {
    echo "ℹ️  Коммит уже существует или нет изменений"
}

# Переименование ветки в main
echo ""
echo "🌿 Настройка ветки..."
git branch -M main 2>/dev/null || echo "ℹ️  Ветка уже main"

# Добавление remote (если еще не добавлен)
echo ""
echo "🔗 Настройка remote..."
if ! git remote get-url origin &>/dev/null; then
    git remote add origin https://github.com/MRsaa1/arin-platform.git
    echo "✅ Remote origin добавлен"
else
    echo "ℹ️  Remote origin уже настроен: $(git remote get-url origin)"
    read -p "   Обновить remote? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote set-url origin https://github.com/MRsaa1/arin-platform.git
        echo "✅ Remote обновлен"
    fi
fi

# Финальная проверка
echo ""
echo "📋 Финальная проверка..."
echo ""
echo "Файлы готовые к коммиту:"
git status --short | head -10
echo ""

# Инструкции для push
echo "✅ Готово к публикации!"
echo ""
echo "============================================"
echo "📤 Для загрузки на GitHub выполните:"
echo ""
echo "   git push -u origin main"
echo ""
echo "Или используйте один из вариантов:"
echo ""
echo "1. GitHub CLI:"
echo "   gh auth login"
echo "   git push -u origin main"
echo ""
echo "2. SSH ключ:"
echo "   git remote set-url origin git@github.com:MRsaa1/arin-platform.git"
echo "   git push -u origin main"
echo ""
echo "3. Personal Access Token:"
echo "   git push -u origin main"
echo "   (при запросе username: MRsaa1, password: ваш токен)"
echo ""
echo "============================================"


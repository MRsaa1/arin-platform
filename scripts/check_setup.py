#!/usr/bin/env python3
"""
ARIN Platform - Setup Checker
Проверка готовности окружения для запуска
"""
import sys
import os
from pathlib import Path

def check_python():
    """Проверка версии Python"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (требуется 3.10+)")
        return False

def check_docker():
    """Проверка Docker"""
    import subprocess
    try:
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Docker установлен: {result.stdout.strip()}")
            # Проверка что Docker работает
            result = subprocess.run(['docker', 'ps'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("✅ Docker работает")
                return True
            else:
                print("⚠️  Docker установлен, но не запущен. Запустите Docker Desktop")
                return False
        else:
            print("❌ Docker не установлен")
            return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("❌ Docker не найден")
        return False

def check_env_file():
    """Проверка .env файла"""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        print(f"✅ .env файл найден: {env_path}")
        # Проверка на placeholder значения
        content = env_path.read_text()
        if "CHANGE_THIS" in content:
            print("⚠️  .env содержит placeholder значения - замените их!")
            return False
        return True
    else:
        print("⚠️  .env файл не найден. Создайте из .env.example")
        return False

def check_dependencies():
    """Проверка Python зависимостей"""
    required = ['fastapi', 'uvicorn', 'pydantic', 'sqlalchemy']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} не установлен")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Установите недостающие пакеты:")
        print(f"   pip install {' '.join(missing)}")
        return False
    return True

def main():
    print("=" * 60)
    print("ARIN Platform - Setup Checker")
    print("=" * 60)
    print()
    
    results = {
        "python": check_python(),
        "docker": check_docker(),
        "env": check_env_file(),
        "dependencies": check_dependencies()
    }
    
    print()
    print("=" * 60)
    print("РЕЗУЛЬТАТЫ")
    print("=" * 60)
    
    all_ok = all(results.values())
    
    if all_ok:
        print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ")
        print()
        print("Запуск проекта:")
        print("  Docker: docker-compose up -d")
        print("  Локально: cd backend && uvicorn backend.main:app --reload")
        return 0
    else:
        print("❌ НЕКОТОРЫЕ ПРОВЕРКИ НЕ ПРОЙДЕНЫ")
        print()
        print("Исправьте проблемы выше и запустите проверку снова")
        return 1

if __name__ == "__main__":
    sys.exit(main())


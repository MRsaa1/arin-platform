#!/usr/bin/env python3
"""
ARIN Platform - Production Readiness Verification Script
Проверка готовности системы к production deployment
"""
import sys
import os
from pathlib import Path
import subprocess
import json

# Цвета для вывода
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def check_mark():
    return f"{GREEN}✓{RESET}"

def cross_mark():
    return f"{RED}✗{RESET}"

def warning_mark():
    return f"{YELLOW}⚠{RESET}"

def check_file_exists(filepath: str, required: bool = True) -> bool:
    """Проверка существования файла"""
    exists = Path(filepath).exists()
    if required and not exists:
        print(f"  {cross_mark()} {filepath} - НЕ НАЙДЕН")
    elif exists:
        print(f"  {check_mark()} {filepath}")
    return exists

def check_env_var(var: str, required: bool = True) -> bool:
    """Проверка переменной окружения"""
    value = os.getenv(var)
    if required and not value:
        print(f"  {cross_mark()} {var} - НЕ УСТАНОВЛЕНА")
        return False
    elif value:
        if "password" in var.lower() or "key" in var.lower() or "secret" in var.lower():
            print(f"  {check_mark()} {var} - установлена (скрыта)")
        else:
            print(f"  {check_mark()} {var} - установлена")
        return True
    else:
        print(f"  {warning_mark()} {var} - не установлена (опционально)")
        return True

def check_secrets_in_code() -> bool:
    """Проверка на наличие секретов в коде"""
    print("\n🔒 Проверка безопасности кода...")
    
    # Проверка на реальные API ключи
    issues = []
    
    # Проверка .env файлов в репозитории
    env_files = list(Path(".").rglob(".env"))
    env_files = [f for f in env_files if ".env.example" not in str(f)]
    
    if env_files:
        print(f"  {warning_mark()} Найдены .env файлы (должны быть в .gitignore):")
        for f in env_files:
            print(f"    - {f}")
        issues.append("env_files")
    
    # Проверка на хардкоженные секреты
    secret_patterns = [
        ("sk-", "OpenAI API key"),
        ("nvapi-", "NVIDIA API key"),
        ("password.*=.*['\"][^'\"]{8,}", "Hardcoded password"),
    ]
    
    code_files = list(Path("backend").rglob("*.py"))
    for pattern, description in secret_patterns:
        found = False
        for code_file in code_files:
            try:
                content = code_file.read_text()
                if pattern in content.lower():
                    # Проверяем что это не пример или комментарий
                    if "example" not in content.lower() and "#" not in content[:content.find(pattern)]:
                        if not found:
                            print(f"  {warning_mark()} Потенциальные {description} в коде")
                            found = True
                        issues.append(f"secret_{pattern}")
            except:
                pass
    
    if not issues:
        print(f"  {check_mark()} Секреты не найдены в коде")
        return True
    else:
        print(f"  {cross_mark()} Найдены потенциальные проблемы безопасности")
        return False

def check_documentation() -> bool:
    """Проверка документации"""
    print("\n📚 Проверка документации...")
    
    required_docs = [
        "README.md",
        "docs/user-guide.md",
        "docs/admin-guide.md",
        "docs/deployment-guide.md",
        "docs/troubleshooting-guide.md",
        "docs/faq.md",
        "docs/api-reference.md",
        "SECURITY.md",
        "PRODUCTION_DEPLOYMENT.md"
    ]
    
    all_exist = True
    for doc in required_docs:
        if not check_file_exists(doc, required=True):
            all_exist = False
    
    return all_exist

def check_configuration() -> bool:
    """Проверка конфигурации"""
    print("\n⚙️  Проверка конфигурации...")
    
    config_files = [
        "docker-compose.prod.yml",
        "infrastructure/kubernetes/deployment.yaml",
        "infrastructure/nginx/nginx-ssl.conf",
        ".env.example"
    ]
    
    all_exist = True
    for config in config_files:
        if not check_file_exists(config, required=True):
            all_exist = False
    
    return all_exist

def check_code_quality() -> bool:
    """Проверка качества кода"""
    print("\n💻 Проверка качества кода...")
    
    # Проверка наличия тестов
    test_files = list(Path("backend/tests").rglob("test_*.py"))
    if test_files:
        print(f"  {check_mark()} Найдено {len(test_files)} тестовых файлов")
    else:
        print(f"  {warning_mark()} Тесты не найдены")
    
    # Проверка requirements.txt
    if check_file_exists("backend/requirements.txt"):
        print(f"  {check_mark()} requirements.txt существует")
    
    return True

def main():
    """Основная функция проверки"""
    print("=" * 60)
    print("ARIN Platform - Production Readiness Verification")
    print("=" * 60)
    
    results = {
        "security": False,
        "documentation": False,
        "configuration": False,
        "code_quality": False
    }
    
    # Проверка безопасности
    results["security"] = check_secrets_in_code()
    
    # Проверка документации
    results["documentation"] = check_documentation()
    
    # Проверка конфигурации
    results["configuration"] = check_configuration()
    
    # Проверка качества кода
    results["code_quality"] = check_code_quality()
    
    # Итоговый результат
    print("\n" + "=" * 60)
    print("ИТОГОВЫЙ РЕЗУЛЬТАТ")
    print("=" * 60)
    
    all_passed = all(results.values())
    
    for check, passed in results.items():
        status = check_mark() if passed else cross_mark()
        print(f"{status} {check.upper()}")
    
    print("\n" + "=" * 60)
    if all_passed:
        print(f"{GREEN}✅ СИСТЕМА ГОТОВА К PRODUCTION DEPLOYMENT{RESET}")
        return 0
    else:
        print(f"{RED}❌ СИСТЕМА НЕ ГОТОВА. Исправьте найденные проблемы.{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())


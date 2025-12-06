# 🚀 Как запустить ARIN Platform

## Вариант 1: С Docker (рекомендуется)

### Установка Docker
1. Скачайте Docker Desktop: https://www.docker.com/products/docker-desktop
2. Установите и запустите Docker Desktop

### Запуск
```bash
# Простой запуск
./START_PROJECT.sh

# Или вручную
docker-compose up -d
```

### Проверка
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Вариант 2: Локально (без Docker)

### Требования
- Python 3.10+
- PostgreSQL, Redis, Neo4j (установлены локально)

### Запуск
```bash
# Проверка окружения
python3 scripts/check_setup.py

# Запуск backend
./scripts/run_local.sh
```

## Быстрая проверка

```bash
# Health check
curl http://localhost:8000/health

# Список агентов
curl http://localhost:8000/api/v1/agents
```

## Troubleshooting

### Docker не найден
- Установите Docker Desktop
- Запустите Docker Desktop
- Проверьте: `docker ps`

### Ошибки подключения к БД
- Убедитесь, что все БД запущены
- Проверьте пароли в `.env`
- Проверьте логи

### Порт занят
- Измените порт в `docker-compose.yml` или команде запуска

## Документация

- Полная документация: `docs/`
- API Reference: http://localhost:8000/docs
- Deployment Guide: `PRODUCTION_DEPLOYMENT.md`

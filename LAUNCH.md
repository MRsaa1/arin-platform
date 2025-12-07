# 🚀 Запуск ARIN Platform

## Шаг 1: Перейдите в директорию проекта

```bash
cd ~/arin-platform
# или
cd /Users/artur220513timur110415gmail.com/arin-platform
```

## Шаг 2: Проверьте, что вы в правильной директории

```bash
ls -la docker-compose.yml START_PROJECT.sh
```

Должны увидеть оба файла.

## Шаг 3: Запустите проект

### Вариант A: Через скрипт
```bash
./START_PROJECT.sh
```

### Вариант B: Через docker-compose
```bash
docker-compose up -d
```

### Вариант C: С выводом логов
```bash
docker-compose up
```

## Шаг 4: Проверьте статус

```bash
# Статус контейнеров
docker-compose ps

# Логи backend
docker-compose logs -f backend

# Health check
curl http://localhost:8000/health
```

## Если Docker не установлен

1. Установите Docker Desktop: https://www.docker.com/products/docker-desktop
2. Запустите Docker Desktop
3. Проверьте: `docker ps`

## Troubleshooting

### "no such file or directory"
- Убедитесь, что вы в директории проекта: `cd ~/arin-platform`

### "no configuration file provided"
- Убедитесь, что `docker-compose.yml` существует в текущей директории

### "Docker not found"
- Установите Docker Desktop
- Запустите Docker Desktop
- Проверьте: `docker ps`

# ARIN Platform - Тесты

## Структура тестов

```
tests/
├── unit/              # Unit тесты для отдельных компонентов
│   ├── test_market_risk_agent.py
│   └── test_credit_risk_agent.py
├── integration/       # Integration тесты для API и взаимодействий
│   ├── test_api_agents.py
│   ├── test_api_risks.py
│   └── test_orchestrator.py
├── e2e/               # End-to-end тесты для полных workflow
│   └── test_full_risk_analysis.py
├── test_load.py       # Базовые тесты нагрузки
├── conftest.py        # Pytest конфигурация и фикстуры
└── README.md          # Этот файл
```

## Запуск тестов

### Все тесты
```bash
pytest
```

### Только unit тесты
```bash
pytest tests/unit -m unit
```

### Только integration тесты
```bash
pytest tests/integration -m integration
```

### Только e2e тесты
```bash
pytest tests/e2e -m e2e
```

### Тесты нагрузки
```bash
pytest tests/test_load.py -m slow
```

### С покрытием кода
```bash
pytest --cov=backend --cov-report=html
```

### Параллельный запуск
```bash
pytest -n auto
```

## Маркеры тестов

- `@pytest.mark.unit` - Unit тесты
- `@pytest.mark.integration` - Integration тесты
- `@pytest.mark.e2e` - End-to-end тесты
- `@pytest.mark.slow` - Медленные тесты
- `@pytest.mark.requires_db` - Требуют базу данных
- `@pytest.mark.requires_redis` - Требуют Redis
- `@pytest.mark.requires_api` - Требуют внешние API

## Примеры использования

### Запуск только быстрых тестов
```bash
pytest -m "not slow"
```

### Запуск тестов без внешних зависимостей
```bash
pytest -m "not requires_db and not requires_redis and not requires_api"
```

## Покрытие кода

Цель: **>70% покрытия** для критических компонентов

Текущее покрытие можно проверить:
```bash
pytest --cov=backend --cov-report=term-missing
```

HTML отчет:
```bash
pytest --cov=backend --cov-report=html
open htmlcov/index.html
```

## CI/CD

Тесты автоматически запускаются в CI/CD pipeline:
- При каждом push в main/develop
- При создании pull request
- Перед деплоем

## Примечания

- Unit тесты не требуют внешних зависимостей (БД, Redis, API)
- Integration тесты могут требовать запущенные сервисы
- E2E тесты требуют полную инфраструктуру
- Тесты нагрузки помечены как `slow` и требуют больше времени


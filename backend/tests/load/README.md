# ARIN Platform - Load Testing

## Обзор

Набор скриптов для нагрузочного и стресс-тестирования ARIN Platform.

## Скрипты

### 1. Load Test (`load_test.py`)

Базовое нагрузочное тестирование системы.

**Параметры**:
- Concurrent users: 100
- Requests per user: 10
- Total requests: 1000

**Метрики**:
- Success rate
- Requests per second
- Response times (mean, median, p95, p99)
- Status codes distribution

**Запуск**:
```bash
python load_test.py
```

**Результаты**: Сохраняются в `load_test_results.json`

### 2. Stress Test (`stress_test.py`)

Стресс-тестирование для выявления пределов системы.

**Тесты**:
1. **Gradual Load**: Постепенное увеличение нагрузки (10-500 users)
2. **Spike Load**: Резкий скачок нагрузки (1000 users)

**Запуск**:
```bash
python stress_test.py
```

**Результаты**: Сохраняются в `stress_test_results.json`

### 3. Bottleneck Analyzer (`bottleneck_analyzer.py`)

Анализ узких мест в системе.

**Анализ**:
- Медленные endpoints (>500ms)
- Критические узкие места (>1s)
- Endpoints с ошибками

**Запуск**:
```bash
python bottleneck_analyzer.py
```

**Результаты**: Сохраняются в `bottleneck_report.json`

## Настройка

Перед запуском тестов убедитесь, что:

1. Backend запущен и доступен на `http://localhost:8000`
2. Все зависимости установлены:
   ```bash
   pip install aiohttp
   ```
3. Система находится в стабильном состоянии

## Интерпретация результатов

### Load Test

- **Success rate > 95%**: Отлично
- **Success rate 90-95%**: Хорошо
- **Success rate < 90%**: Требует оптимизации

- **P95 < 500ms**: Отлично
- **P95 500-1000ms**: Хорошо
- **P95 > 1000ms**: Требует оптимизации

### Stress Test

- **Maximum users**: Максимальное количество пользователей, которое система может обработать
- **Best throughput**: Лучшая пропускная способность
- **Degradation point**: Точка деградации системы

### Bottleneck Analyzer

- **Critical bottlenecks**: Критические узкие места, требующие немедленного внимания
- **Slow endpoints**: Медленные endpoints, которые можно оптимизировать
- **Error-prone endpoints**: Endpoints с высоким процентом ошибок

## Рекомендации

1. Запускайте тесты регулярно после изменений
2. Сравнивайте результаты между версиями
3. Фокусируйтесь на устранении критических узких мест
4. Мониторьте метрики в production


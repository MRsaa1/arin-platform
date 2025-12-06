# ARIN Platform - LLM Integration

## Обзор

Централизованная система управления LLM интеграциями с поддержкой:
- Кэширования ответов
- Retry логики
- Автоматического переключения между провайдерами
- Специализированных промптов для каждого агента
- Извлечения структурированных данных

## Архитектура

### LLMManager

Центральный менеджер для всех LLM операций:

```python
from backend.ai_engine.llm import LLMManager

llm_manager = LLMManager()

# Генерация ответа
response = await llm_manager.generate(
    prompt="Анализ кредитного риска...",
    agent_type="credit_risk",
    use_reasoning=True,  # Использовать DeepSeek R1 для reasoning
    use_cache=True
)

print(response.content)
print(response.reasoning)  # Процесс рассуждения (DeepSeek R1)
```

### Провайдеры

Приоритет для reasoning задач:
1. **DeepSeek R1 (NVIDIA)** - лучший для reasoning
2. GPT-4 - fallback
3. GPT-4 Turbo - fallback

Приоритет для обычных задач:
1. GPT-4
2. GPT-4 Turbo
3. DeepSeek R1

### Кэширование

Автоматическое кэширование ответов на 24 часа:
- Снижает затраты на API вызовы
- Ускоряет повторные запросы
- Ключ кэша основан на промпте и параметрах

### Retry логика

- Максимум 3 попытки для каждого провайдера
- Экспоненциальная задержка между попытками
- Автоматическое переключение на следующий провайдер при ошибке

## Использование в агентах

### Пример: Credit Risk Agent

```python
from backend.ai_engine.llm import PromptTemplates

# Использование специализированного промпта
prompt = PromptTemplates.credit_risk_analysis(
    entity_name="Company Inc.",
    financial_metrics={...},
    credit_history={...},
    pd_score=0.05
)

response = await self.llm_manager.generate(
    prompt=prompt,
    agent_type="credit_risk",
    use_reasoning=True
)
```

## Извлечение структурированных данных

```python
schema = {
    "type": "object",
    "properties": {
        "risk_score": {"type": "number"},
        "factors": {"type": "array"},
        "recommendations": {"type": "array"}
    }
}

data = await llm_manager.extract_structured_data(
    text="Неструктурированный текст...",
    schema=schema,
    agent_type="credit_risk"
)
```

## API Endpoints

- `POST /api/v1/llm/generate` - Генерация ответа
- `POST /api/v1/llm/extract` - Извлечение структурированных данных
- `GET /api/v1/llm/cache/stats` - Статистика кэша
- `POST /api/v1/llm/cache/clear` - Очистка кэша

## Конфигурация

Настройки в `config.py`:
- `nvidia_api_key` - для DeepSeek R1
- `openai_api_key` - для GPT-4

## Специализированные промпты

Каждый тип агента имеет свой шаблон промпта:
- `credit_risk_analysis` - для Credit Risk Agent
- `market_risk_analysis` - для Market Risk Agent
- `operational_risk_analysis` - для Operational Risk Agent
- `liquidity_risk_analysis` - для Liquidity Risk Agent
- `regulatory_risk_analysis` - для Regulatory Risk Agent
- `systemic_risk_analysis` - для Systemic Risk Agent


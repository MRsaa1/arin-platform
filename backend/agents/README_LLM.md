# LLM Интеграция в ARIN Agents

## Стратегия использования LLM

### Приоритет: DeepSeek R1 через NVIDIA API

**Почему DeepSeek R1?**
- ✅ Специализирован на reasoning задачах
- ✅ Показывает процесс рассуждения (reasoning_content)
- ✅ Лучше для финансового анализа, требующего глубокого анализа
- ✅ Бесплатный через NVIDIA API
- ✅ OpenAI-совместимый API

### Fallback: GPT-4

- Используется если DeepSeek R1 недоступен
- Хорошее качество, но не специализирован на reasoning

## Использование DeepSeek R1

### Конфигурация

```env
# .env файл
NVIDIA_API_KEY=your-nvidia-api-key
```

### Код

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="your-nvidia-api-key"
)

completion = client.chat.completions.create(
    model="deepseek-ai/deepseek-r1",
    messages=[{"role": "user", "content": "..."}],
    temperature=0.6,
    top_p=0.7,
    max_tokens=4096,
    stream=True
)

# Сбор reasoning и content
reasoning_parts = []
content_parts = []

for chunk in completion:
    reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
    if reasoning:
        reasoning_parts.append(reasoning)
    
    if chunk.choices[0].delta.content is not None:
        content_parts.append(chunk.choices[0].delta.content)

reasoning_text = "".join(reasoning_parts)
final_answer = "".join(content_parts)
```

## Преимущества DeepSeek R1 для финансового анализа

1. **Глубокий анализ**: Может анализировать сложные взаимосвязи
2. **Процесс рассуждения**: Показывает как пришел к выводу
3. **Точность**: Лучше для задач требующих логического анализа
4. **Бесплатно**: Через NVIDIA API

## Пример использования в Credit Risk Agent

Credit Risk Agent использует DeepSeek R1 для:
- Анализа кредитного риска
- Выявления ключевых факторов риска
- Генерации рекомендаций с обоснованием
- Анализа взаимосвязей между финансовыми метриками


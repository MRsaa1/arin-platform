"""
ARIN Platform - LLM Manager
Централизованное управление LLM интеграциями с кэшированием, retry логикой и multi-LLM поддержкой
"""
import logging
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime, timedelta
import hashlib
import json
from enum import Enum

from backend.config import settings

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """Провайдеры LLM"""
    DEEPSEEK_R1_NVIDIA = "deepseek-r1-nvidia"  # Приоритет для reasoning
    GPT_4 = "gpt-4"  # Fallback
    GPT_4_TURBO = "gpt-4-turbo"
    CLAUDE = "claude"  # Опционально


class LLMResponse:
    """Ответ от LLM"""
    def __init__(
        self,
        content: str,
        provider: LLMProvider,
        reasoning: Optional[str] = None,
        model: Optional[str] = None,
        tokens_used: Optional[int] = None,
        cached: bool = False
    ):
        self.content = content
        self.provider = provider
        self.reasoning = reasoning
        self.model = model
        self.tokens_used = tokens_used
        self.cached = cached
        self.timestamp = datetime.now()


class LLMManager:
    """
    Менеджер для управления LLM интеграциями
    
    Функции:
    - Кэширование ответов
    - Retry логика
    - Автоматическое переключение между провайдерами
    - Специализированные промпты
    """
    
    def __init__(self):
        """Инициализация LLM Manager"""
        self.clients = {}
        self.cache = {}  # Простое in-memory кэширование (в production использовать Redis)
        self.cache_ttl = timedelta(hours=24)  # TTL для кэша
        self.max_retries = 3
        self.retry_delay = 1.0  # секунды
        
        # Приоритет провайдеров для reasoning задач
        self.reasoning_providers = [
            LLMProvider.DEEPSEEK_R1_NVIDIA,
            LLMProvider.GPT_4,
            LLMProvider.GPT_4_TURBO
        ]
        
        # Приоритет провайдеров для обычных задач
        self.general_providers = [
            LLMProvider.GPT_4,
            LLMProvider.GPT_4_TURBO,
            LLMProvider.DEEPSEEK_R1_NVIDIA
        ]
        
        self._initialize_clients()
        
    def _initialize_clients(self):
        """Инициализация клиентов для всех провайдеров"""
        try:
            # DeepSeek R1 через NVIDIA API (приоритет для reasoning)
            if settings.nvidia_api_key:
                try:
                    from openai import OpenAI
                    self.clients[LLMProvider.DEEPSEEK_R1_NVIDIA] = OpenAI(
                        base_url="https://integrate.api.nvidia.com/v1",
                        api_key=settings.nvidia_api_key
                    )
                    logger.info("DeepSeek R1 (NVIDIA) client initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize DeepSeek R1 client: {e}")
            
            # GPT-4 (fallback)
            if settings.openai_api_key:
                try:
                    from openai import OpenAI
                    self.clients[LLMProvider.GPT_4] = OpenAI(api_key=settings.openai_api_key)
                    self.clients[LLMProvider.GPT_4_TURBO] = OpenAI(api_key=settings.openai_api_key)
                    logger.info("OpenAI (GPT-4) clients initialized")
                except Exception as e:
                    logger.warning(f"Failed to initialize OpenAI clients: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to initialize LLM clients: {e}")
            
    def _get_cache_key(self, prompt: str, provider: LLMProvider, **kwargs) -> str:
        """Генерация ключа кэша"""
        cache_data = {
            "prompt": prompt,
            "provider": provider.value,
            **kwargs
        }
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_string.encode()).hexdigest()
        
    def _get_from_cache(self, cache_key: str) -> Optional[LLMResponse]:
        """Получение из кэша"""
        if cache_key in self.cache:
            cached_item = self.cache[cache_key]
            if datetime.now() - cached_item["timestamp"] < self.cache_ttl:
                logger.debug(f"Cache hit for key: {cache_key[:8]}...")
                response = cached_item["response"]
                response.cached = True
                return response
            else:
                # Удаление устаревшего кэша
                del self.cache[cache_key]
        return None
        
    def _save_to_cache(self, cache_key: str, response: LLMResponse):
        """Сохранение в кэш"""
        self.cache[cache_key] = {
            "response": response,
            "timestamp": datetime.now()
        }
        logger.debug(f"Cached response for key: {cache_key[:8]}...")
        
    async def generate(
        self,
        prompt: str,
        agent_type: str = "general",
        use_reasoning: bool = False,
        use_cache: bool = True,
        temperature: float = 0.6,
        max_tokens: int = 2048,
        **kwargs
    ) -> LLMResponse:
        """
        Генерация ответа от LLM
        
        Args:
            prompt: Промпт
            agent_type: Тип агента (для специализированных промптов)
            use_reasoning: Использовать reasoning модель (DeepSeek R1)
            use_cache: Использовать кэш
            temperature: Temperature для генерации
            max_tokens: Максимальное количество токенов
            **kwargs: Дополнительные параметры
            
        Returns:
            LLMResponse
        """
        # Выбор провайдеров
        providers = self.reasoning_providers if use_reasoning else self.general_providers
        
        # Проверка кэша
        if use_cache:
            for provider in providers:
                cache_key = self._get_cache_key(prompt, provider, **kwargs)
                cached_response = self._get_from_cache(cache_key)
                if cached_response:
                    return cached_response
        
        # Попытка генерации с retry логикой
        last_error = None
        for provider in providers:
            if provider not in self.clients:
                continue
                
            for attempt in range(self.max_retries):
                try:
                    response = await self._generate_with_provider(
                        provider=provider,
                        prompt=prompt,
                        agent_type=agent_type,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        **kwargs
                    )
                    
                    # Сохранение в кэш
                    if use_cache:
                        cache_key = self._get_cache_key(prompt, provider, **kwargs)
                        self._save_to_cache(cache_key, response)
                    
                    return response
                    
                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"Attempt {attempt + 1}/{self.max_retries} failed for {provider.value}: {e}"
                    )
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
        
        # Все попытки провалились
        logger.error(f"All LLM providers failed. Last error: {last_error}")
        raise Exception(f"Failed to generate response from any LLM provider: {last_error}")
        
    async def _generate_with_provider(
        self,
        provider: LLMProvider,
        prompt: str,
        agent_type: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> LLMResponse:
        """Генерация с конкретным провайдером"""
        client = self.clients[provider]
        
        # Специализированные промпты для агентов
        enhanced_prompt = self._enhance_prompt_for_agent(prompt, agent_type)
        
        if provider == LLMProvider.DEEPSEEK_R1_NVIDIA:
            # DeepSeek R1 через NVIDIA API
            completion = await asyncio.to_thread(
                client.chat.completions.create,
                model="deepseek-ai/deepseek-r1",
                messages=[{"role": "user", "content": enhanced_prompt}],
                temperature=temperature,
                top_p=0.7,
                max_tokens=max_tokens,
                stream=False
            )
            
            reasoning_content = getattr(completion.choices[0].message, "reasoning_content", None)
            content = completion.choices[0].message.content
            
            return LLMResponse(
                content=content,
                provider=provider,
                reasoning=reasoning_content,
                model="deepseek-ai/deepseek-r1",
                tokens_used=getattr(completion, "usage", {}).get("total_tokens")
            )
            
        elif provider in [LLMProvider.GPT_4, LLMProvider.GPT_4_TURBO]:
            # GPT-4
            model_name = "gpt-4-turbo-preview" if provider == LLMProvider.GPT_4_TURBO else "gpt-4"
            
            completion = await asyncio.to_thread(
                client.chat.completions.create,
                model=model_name,
                messages=[{"role": "user", "content": enhanced_prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return LLMResponse(
                content=completion.choices[0].message.content,
                provider=provider,
                model=model_name,
                tokens_used=completion.usage.total_tokens if hasattr(completion, "usage") else None
            )
            
        else:
            raise ValueError(f"Unsupported provider: {provider}")
            
    def _enhance_prompt_for_agent(self, prompt: str, agent_type: str) -> str:
        """
        Улучшение промпта для конкретного типа агента
        
        Args:
            prompt: Исходный промпт
            agent_type: Тип агента
            
        Returns:
            Улучшенный промпт
        """
        # Специализированные инструкции для каждого типа агента
        agent_instructions = {
            "credit_risk": """
Ты - эксперт по анализу кредитных рисков. Твоя задача:
1. Оценить кредитоспособность на основе финансовых данных
2. Выявить признаки потенциального дефолта
3. Предоставить структурированный анализ с конкретными метриками
4. Дать приоритизированные рекомендации

Формат ответа должен быть структурированным и содержать:
- Оценку риска (высокий/средний/низкий)
- Ключевые факторы риска
- Рекомендации по снижению риска
""",
            "market_risk": """
Ты - эксперт по анализу рыночных рисков. Твоя задача:
1. Проанализировать волатильность и корреляции
2. Оценить потенциальные потери (VaR, CVaR)
3. Выявить рыночные тренды и паттерны
4. Предоставить рекомендации по управлению портфелем

Формат ответа должен быть структурированным и содержать:
- Оценку рыночного риска
- Ключевые факторы волатильности
- Рекомендации по хеджированию
""",
            "operational_risk": """
Ты - эксперт по операционным рискам. Твоя задача:
1. Выявить уязвимости в операционных процессах
2. Оценить вероятность операционных сбоев
3. Проанализировать эффективность процессов
4. Предоставить рекомендации по улучшению

Формат ответа должен быть структурированным и содержать:
- Выявленные уязвимости
- Оценку вероятности сбоев
- Приоритетные рекомендации
""",
            "liquidity_risk": """
Ты - эксперт по рискам ликвидности. Твоя задача:
1. Оценить текущую ликвидность
2. Проанализировать соответствие регуляторным требованиям (LCR, NSFR)
3. Выявить потенциальные проблемы с ликвидностью
4. Предоставить рекомендации по управлению ликвидностью

Формат ответа должен быть структурированным и содержать:
- Оценку ликвидности
- Соответствие требованиям
- Рекомендации по улучшению
""",
            "regulatory_risk": """
Ты - эксперт по регуляторным рискам. Твоя задача:
1. Оценить соответствие регуляторным требованиям
2. Выявить риски несоответствия
3. Проанализировать изменения в регуляциях
4. Предоставить рекомендации по compliance

Формат ответа должен быть структурированным и содержать:
- Оценку соответствия
- Выявленные риски
- Рекомендации по compliance
""",
            "systemic_risk": """
Ты - эксперт по системным рискам. Твоя задача:
1. Проанализировать взаимосвязи между рисками
2. Выявить каскадные эффекты
3. Оценить концентрацию рисков
4. Предоставить рекомендации по снижению системного риска

Формат ответа должен быть структурированным и содержать:
- Анализ взаимосвязей
- Выявленные каскадные эффекты
- Рекомендации по диверсификации
"""
        }
        
        instruction = agent_instructions.get(agent_type, "")
        
        if instruction:
            return f"{instruction}\n\n{prompt}"
        return prompt
        
    async def extract_structured_data(
        self,
        text: str,
        schema: Dict[str, Any],
        agent_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Извлечение структурированных данных из неструктурированного текста
        
        Args:
            text: Неструктурированный текст
            schema: Схема для извлечения данных
            agent_type: Тип агента
            
        Returns:
            Структурированные данные
        """
        schema_description = json.dumps(schema, indent=2)
        
        prompt = f"""
Извлеки структурированные данные из следующего текста согласно схеме:

Схема:
{schema_description}

Текст:
{text}

Верни только JSON объект, соответствующий схеме. Не добавляй пояснений.
"""
        
        response = await self.generate(
            prompt=prompt,
            agent_type=agent_type,
            use_reasoning=False,  # Для структурированного извлечения reasoning не нужен
            temperature=0.1  # Низкая temperature для более детерминированного вывода
        )
        
        try:
            # Парсинг JSON из ответа
            content = response.content.strip()
            # Удаление markdown code blocks если есть
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1])
            elif content.startswith("```json"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1])
                
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            logger.error(f"Response content: {response.content[:500]}")
            return {}
            
    def clear_cache(self):
        """Очистка кэша"""
        self.cache.clear()
        logger.info("LLM cache cleared")
        
    def get_cache_stats(self) -> Dict[str, Any]:
        """Получение статистики кэша"""
        total_items = len(self.cache)
        valid_items = sum(
            1 for item in self.cache.values()
            if datetime.now() - item["timestamp"] < self.cache_ttl
        )
        
        return {
            "total_items": total_items,
            "valid_items": valid_items,
            "expired_items": total_items - valid_items,
            "cache_ttl_hours": self.cache_ttl.total_seconds() / 3600
        }


"""
ARIN Platform - LLM Management API Endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from backend.ai_engine.llm import LLMManager

router = APIRouter()

# Глобальный экземпляр LLM Manager (будет инициализирован в main.py)
llm_manager: Optional[LLMManager] = None


class LLMGenerateRequest(BaseModel):
    """Запрос на генерацию LLM ответа"""
    prompt: str
    agent_type: str = "general"
    use_reasoning: bool = False
    use_cache: bool = True
    temperature: float = 0.6
    max_tokens: int = 2048


class ExtractDataRequest(BaseModel):
    """Запрос на извлечение структурированных данных"""
    text: str
    schema: dict
    agent_type: str = "general"


@router.post("/generate")
async def generate_llm_response(request: LLMGenerateRequest):
    """Генерация LLM ответа"""
    if not llm_manager:
        raise HTTPException(status_code=503, detail="LLM Manager not initialized")
    
    try:
        response = await llm_manager.generate(
            prompt=request.prompt,
            agent_type=request.agent_type,
            use_reasoning=request.use_reasoning,
            use_cache=request.use_cache,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return {
            "content": response.content,
            "reasoning": response.reasoning,
            "model": response.model or response.provider.value,
            "cached": response.cached,
            "tokens_used": response.tokens_used
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract")
async def extract_structured_data(request: ExtractDataRequest):
    """Извлечение структурированных данных из текста"""
    if not llm_manager:
        raise HTTPException(status_code=503, detail="LLM Manager not initialized")
    
    try:
        data = await llm_manager.extract_structured_data(
            text=request.text,
            schema=request.schema,
            agent_type=request.agent_type
        )
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cache/stats")
async def get_cache_stats():
    """Получить статистику кэша"""
    if not llm_manager:
        raise HTTPException(status_code=503, detail="LLM Manager not initialized")
    
    return llm_manager.get_cache_stats()


@router.post("/cache/clear")
async def clear_cache():
    """Очистить кэш LLM"""
    if not llm_manager:
        raise HTTPException(status_code=503, detail="LLM Manager not initialized")
    
    llm_manager.clear_cache()
    return {"message": "Cache cleared"}


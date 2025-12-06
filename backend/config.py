"""
ARIN Platform - Configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Application
    app_name: str = "ARIN Platform"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Database
    # ⚠️ ВАЖНО: Используйте переменные окружения DATABASE_URL и TIMESCALEDB_URL
    database_url: str = ""  # Должен быть установлен через DATABASE_URL env var
    timescaledb_url: str = ""  # Должен быть установлен через TIMESCALEDB_URL env var
    redis_url: str = "redis://localhost:6379"
    
    # Neo4j
    neo4j_url: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = ""  # Должен быть установлен через NEO4J_PASSWORD env var
    
    # API Keys
    # Приоритет: DeepSeek R1 через NVIDIA API для reasoning задач, GPT-4 как fallback
    nvidia_api_key: Optional[str] = None  # DeepSeek R1 через NVIDIA API - лучший для reasoning
    openai_api_key: Optional[str] = None  # GPT-4 - fallback
    
    # NVIDIA API (используется для DeepSeek R1 и других NVIDIA моделей)
    nvidia_api_key: Optional[str] = None  # Используется для DeepSeek R1 reasoning
    nvidia_nim_endpoint: str = "https://integrate.api.nvidia.com/v1"
    nvidia_cuopt_endpoint: str = "https://cuopt.api.nvidia.com/v1"
    
    # NVIDIA Models
    nvidia_reasoning_model: str = "nvidia-nemotron-nano-9b-v2"
    nvidia_embedding_model: str = "llama-3_2-nemoretriever-300m-embed-v2"
    nvidia_rerank_model: str = "llama-3.2-nemoretriever-500m-rerank-v2"
    nvidia_parse_model: str = "nemotron-parse"
    
    # Security
    # ⚠️ ВАЖНО: Сгенерируйте уникальный SECRET_KEY для production!
    secret_key: str = ""  # Должен быть установлен через SECRET_KEY env var
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # External Integrations (Optional)
    risk_analyzer_url: Optional[str] = None
    news_analytics_url: Optional[str] = None
    investment_dashboard_url: Optional[str] = None
    crypto_analytics_url: Optional[str] = None
    
    # External Data Sources API Keys
    fred_api_key: Optional[str] = None  # FRED API key (https://fred.stlouisfed.org/docs/api/api_key.html)
    
    # Agent Settings
    agent_polling_interval: int = 5  # seconds
    agent_timeout: int = 300  # seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Глобальный экземпляр настроек
settings = Settings()


"""
Pytest configuration and fixtures
"""
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock, MagicMock
import os

# Настройка переменных окружения для тестов
os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("LOG_LEVEL", "DEBUG")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/test_arin")
os.environ.setdefault("NEO4J_URI", "bolt://localhost:7687")
os.environ.setdefault("NEO4J_USER", "neo4j")
os.environ.setdefault("NEO4J_PASSWORD", "test")


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Создание event loop для тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_redis() -> Mock:
    """Mock Redis клиент"""
    redis_mock = Mock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock(return_value=True)
    redis_mock.delete = AsyncMock(return_value=True)
    redis_mock.publish = AsyncMock(return_value=True)
    redis_mock.subscribe = AsyncMock(return_value=Mock())
    return redis_mock


@pytest.fixture
def mock_db_engine() -> Mock:
    """Mock database engine"""
    engine_mock = Mock()
    engine_mock.connect = Mock(return_value=Mock())
    engine_mock.execute = Mock(return_value=Mock())
    return engine_mock


@pytest.fixture
def mock_llm_client() -> Mock:
    """Mock LLM клиент (OpenAI/NVIDIA)"""
    client_mock = Mock()
    
    # Mock для chat.completions.create
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].delta = Mock()
    mock_response.choices[0].delta.content = "Test response"
    mock_response.choices[0].delta.reasoning_content = "Test reasoning"
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = "Test response"
    
    client_mock.chat = Mock()
    client_mock.chat.completions = Mock()
    client_mock.chat.completions.create = AsyncMock(return_value=mock_response)
    
    return client_mock


@pytest.fixture
def sample_market_data() -> dict:
    """Пример рыночных данных для тестов"""
    return {
        "symbol": "AAPL",
        "prices": [100.0, 102.5, 101.0, 103.0, 105.0],
        "dates": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
        "volume": [1000000, 1200000, 1100000, 1300000, 1400000]
    }


@pytest.fixture
def sample_credit_data() -> dict:
    """Пример кредитных данных для тестов"""
    return {
        "entity_id": "test_entity_001",
        "entity_name": "Test Company Inc.",
        "financial_metrics": {
            "revenue": 1000000,
            "debt": 500000,
            "equity": 500000,
            "ebitda": 200000
        },
        "credit_history": {
            "defaults": 0,
            "late_payments": 2,
            "credit_score": 750
        }
    }


@pytest.fixture
def sample_risk_analysis_task() -> dict:
    """Пример задачи для анализа рисков"""
    return {
        "task_id": "test_task_001",
        "task_type": "risk_analysis",
        "entity_id": "test_entity_001",
        "parameters": {
            "confidence_level": 0.95,
            "time_horizon": 1,
            "portfolio_value": 1000000
        },
        "timestamp": "2024-01-01T00:00:00Z"
    }


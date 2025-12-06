"""
Integration tests for Orchestrator
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from backend.orchestrator.orchestrator import Orchestrator
from backend.agents.market_risk_agent import MarketRiskAgent
from backend.agents.credit_risk_agent import CreditRiskAgent


@pytest.mark.integration
class TestOrchestrator:
    """Тесты для Orchestrator"""
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self):
        """Тест инициализации Orchestrator"""
        orchestrator = Orchestrator()
        
        await orchestrator.initialize()
        
        # Проверяем, что агенты зарегистрированы
        statuses = await orchestrator.get_agent_status()
        assert len(statuses) > 0
        
    @pytest.mark.asyncio
    async def test_distribute_task(self):
        """Тест распределения задачи"""
        orchestrator = Orchestrator()
        await orchestrator.initialize()
        
        task = {
            "task_id": "test_task_001",
            "type": "market_risk",
            "entity_id": "test_portfolio_001",
            "entity_type": "portfolio",
            "required_agents": ["market_risk_agent"],
            "parameters": {
                "confidence_level": 0.95,
                "time_horizon": 1
            }
        }
        
        result = await orchestrator.distribute_task(task)
        
        assert result is not None
        assert "task_id" in result
        assert "overall_status" in result
        
    @pytest.mark.asyncio
    async def test_get_agent_status(self):
        """Тест получения статуса агента"""
        orchestrator = Orchestrator()
        await orchestrator.initialize()
        
        status = await orchestrator.get_agent_status("market_risk_agent")
        
        assert status is not None
        assert "agent_id" in status or "error" in status
        
    @pytest.mark.asyncio
    async def test_unregister_agent(self):
        """Тест отмены регистрации агента"""
        orchestrator = Orchestrator()
        await orchestrator.initialize()
        
        await orchestrator.unregister_agent("market_risk_agent")
        
        # Проверяем, что агент удален
        status = await orchestrator.get_agent_status("market_risk_agent")
        assert "error" in status


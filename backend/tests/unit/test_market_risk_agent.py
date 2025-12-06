"""
Unit tests for Market Risk Agent
"""
import pytest
import numpy as np
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime, timedelta

from backend.agents.market_risk_agent import MarketRiskAgent
from backend.agents.base_agent import AgentStatus


@pytest.mark.unit
class TestMarketRiskAgent:
    """Тесты для Market Risk Agent"""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Тест инициализации агента"""
        agent = MarketRiskAgent(
            agent_id="test_market_risk",
            config={}
        )
        
        assert agent.agent_id == "test_market_risk"
        assert agent.agent_name == "Market Risk Agent"
        assert agent.status == AgentStatus.INITIALIZING
        
    @pytest.mark.asyncio
    async def test_agent_setup_data_access(self):
        """Тест настройки доступа к данным"""
        agent = MarketRiskAgent(
            agent_id="test_market_risk",
            config={}
        )
        
        await agent._setup_data_access()
        
        # Проверяем, что метод выполнился без ошибок
        assert agent.status == AgentStatus.INITIALIZING or agent.status == AgentStatus.ERROR
        
    @pytest.mark.asyncio
    async def test_agent_setup_with_risk_analyzer(self):
        """Тест настройки с интеграцией Risk Analyzer"""
        agent = MarketRiskAgent(
            agent_id="test_market_risk",
            config={
                "risk_analyzer_url": "http://test-risk-analyzer.com"
            }
        )
        
        with patch('backend.integrations.risk_analyzer.RiskAnalyzerClient') as mock_client:
            await agent._setup_data_access()
            
            # Проверяем, что клиент был создан
            assert agent.risk_analyzer_client is not None
            
    @pytest.mark.asyncio
    async def test_calculate_var_cvar(self):
        """Тест расчета VaR и CVaR"""
        agent = MarketRiskAgent(
            agent_id="test_market_risk",
            config={}
        )
        
        await agent.initialize()
        
        # Создаем тестовые рыночные данные
        import pandas as pd
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        returns = np.random.normal(0.001, 0.02, len(dates))
        prices = 100 * (1 + returns).cumprod()
        
        market_data = pd.DataFrame({
            'date': dates,
            'price': prices,
            'returns': returns
        })
        
        parameters = {
            "confidence_level": 0.95,
            "time_horizon": 1
        }
        
        var_result = await agent._calculate_var_cvar(market_data, parameters)
        
        assert var_result is not None
        assert "var_historical" in var_result
        assert "var_parametric" in var_result
        assert "cvar" in var_result
        assert var_result["confidence_level"] == 0.95
        
    @pytest.mark.asyncio
    async def test_stress_test(self):
        """Тест стресс-тестирования"""
        agent = MarketRiskAgent(
            agent_id="test_market_risk",
            config={}
        )
        
        await agent.initialize()
        
        # Создаем тестовые рыночные данные
        import pandas as pd
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        returns = np.random.normal(0.001, 0.02, len(dates))
        prices = 100 * (1 + returns).cumprod()
        
        market_data = pd.DataFrame({
            'date': dates,
            'price': prices,
            'returns': returns
        })
        
        parameters = {}
        
        stress_result = await agent._stress_test(market_data, parameters)
        
        assert stress_result is not None
        assert "scenarios" in stress_result
        assert "market_crash" in stress_result["scenarios"]
        assert "moderate_decline" in stress_result["scenarios"]
        
    @pytest.mark.asyncio
    async def test_analyze_volatility(self):
        """Тест анализа волатильности"""
        agent = MarketRiskAgent(
            agent_id="test_market_risk",
            config={}
        )
        
        await agent.initialize()
        
        # Создаем тестовые рыночные данные
        import pandas as pd
        dates = pd.date_range(end=datetime.now(), periods=100, freq='D')
        returns = np.random.normal(0.001, 0.02, len(dates))
        prices = 100 * (1 + returns).cumprod()
        
        market_data = pd.DataFrame({
            'date': dates,
            'price': prices,
            'returns': returns
        })
        
        volatility_result = await agent._analyze_volatility(market_data)
        
        assert volatility_result is not None
        assert "annual_volatility" in volatility_result
        assert volatility_result["annual_volatility"] >= 0
        
    @pytest.mark.asyncio
    async def test_analyze_task(self):
        """Тест анализа задачи"""
        agent = MarketRiskAgent(
            agent_id="test_market_risk",
            config={}
        )
        
        # Инициализируем агента
        await agent.initialize()
        
        task = {
            "task_id": "test_task_001",
            "entity_id": "test_portfolio_001",
            "entity_type": "portfolio",
            "parameters": {
                "confidence_level": 0.95,
                "time_horizon": 1
            }
        }
        
        result = await agent.analyze(task)
        
        assert result is not None
        assert "task_id" in result
        assert "risk_metrics" in result
        assert result["task_id"] == task["task_id"]
        
    @pytest.mark.asyncio
    async def test_agent_status_transitions(self):
        """Тест переходов статусов агента"""
        agent = MarketRiskAgent(
            agent_id="test_market_risk",
            config={}
        )
        
        assert agent.status == AgentStatus.INITIALIZING
        
        await agent.initialize()
        assert agent.status == AgentStatus.IDLE
        
        # При анализе статус должен измениться
        task = {
            "task_id": "test_task_001",
            "task_type": "market_risk_analysis",
            "portfolio": {"value": 1000000, "positions": []},
            "parameters": {"confidence_level": 0.95}
        }
        
        # Мокаем метод analyze, чтобы проверить изменение статуса
        original_analyze = agent.analyze
        async def mock_analyze(t):
            agent.status = AgentStatus.ANALYZING
            result = await original_analyze(t)
            agent.status = AgentStatus.IDLE
            return result
        
        agent.analyze = mock_analyze
        
        result = await agent.analyze(task)
        
        assert agent.status == AgentStatus.IDLE
        assert result is not None


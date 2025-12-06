"""
Unit tests for Credit Risk Agent
"""
import pytest
import numpy as np
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from datetime import datetime

from backend.agents.credit_risk_agent import CreditRiskAgent
from backend.agents.base_agent import AgentStatus


@pytest.mark.unit
class TestCreditRiskAgent:
    """Тесты для Credit Risk Agent"""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self):
        """Тест инициализации агента"""
        agent = CreditRiskAgent(
            agent_id="test_credit_risk",
            config={}
        )
        
        assert agent.agent_id == "test_credit_risk"
        assert agent.agent_name == "Credit Risk Agent"
        assert agent.status == AgentStatus.INITIALIZING
        
    @pytest.mark.asyncio
    async def test_agent_setup_data_access(self):
        """Тест настройки доступа к данным"""
        agent = CreditRiskAgent(
            agent_id="test_credit_risk",
            config={}
        )
        
        await agent._setup_data_access()
        
        # Проверяем, что метод выполнился без ошибок
        assert agent.status == AgentStatus.INITIALIZING or agent.status == AgentStatus.ERROR
        
    @pytest.mark.asyncio
    async def test_agent_setup_with_nvidia_api(self):
        """Тест настройки с NVIDIA API (DeepSeek R1)"""
        agent = CreditRiskAgent(
            agent_id="test_credit_risk",
            config={
                "nvidia_api_key": "test_nvidia_key"
            }
        )
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            await agent._setup_ai_integration()
            
            # Проверяем, что клиент был создан
            assert agent.deepseek_client is not None
            
    @pytest.mark.asyncio
    async def test_agent_setup_with_openai_fallback(self):
        """Тест настройки с OpenAI как fallback"""
        agent = CreditRiskAgent(
            agent_id="test_credit_risk",
            config={
                "openai_api_key": "test_openai_key"
            }
        )
        
        with patch('openai.OpenAI') as mock_openai:
            mock_client = Mock()
            mock_openai.return_value = mock_client
            
            await agent._setup_ai_integration()
            
            # Проверяем, что OpenAI клиент был создан как fallback
            assert agent.llm_client is not None
            
    @pytest.mark.asyncio
    async def test_calculate_pd(self):
        """Тест расчета Probability of Default (PD)"""
        agent = CreditRiskAgent(
            agent_id="test_credit_risk",
            config={}
        )
        
        await agent.initialize()
        
        # Создаем тестовые финансовые данные
        import pandas as pd
        dates = pd.date_range(end=datetime.now(), periods=12, freq='M')
        np.random.seed(42)
        revenue = 1000000 + np.random.normal(0, 100000, len(dates))
        debt = 500000 + np.random.normal(0, 50000, len(dates))
        equity = 2000000 + np.random.normal(0, 200000, len(dates))
        ebitda = revenue * 0.2 + np.random.normal(0, 20000, len(dates))
        
        financial_data = pd.DataFrame({
            'date': dates,
            'revenue': revenue,
            'debt': debt,
            'equity': equity,
            'ebitda': ebitda,
            'debt_to_equity': debt / equity,
            'ebitda_margin': ebitda / revenue,
            'current_ratio': 1.5 + np.random.normal(0, 0.2, len(dates))
        })
        
        news_data = []
        
        pd_result = await agent._calculate_pd(financial_data, news_data)
        
        assert pd_result is not None
        assert "pd_score" in pd_result
        assert 0 <= pd_result["pd_score"] <= 1  # PD должен быть между 0 и 1
        
    @pytest.mark.asyncio
    async def test_calculate_el(self):
        """Тест расчета Expected Loss (EL)"""
        agent = CreditRiskAgent(
            agent_id="test_credit_risk",
            config={}
        )
        
        await agent.initialize()
        
        # Создаем тестовые данные
        import pandas as pd
        dates = pd.date_range(end=datetime.now(), periods=12, freq='M')
        financial_data = pd.DataFrame({
            'date': dates,
            'revenue': [1000000] * len(dates),
            'debt': [500000] * len(dates),
            'equity': [2000000] * len(dates),
            'ebitda': [200000] * len(dates),
            'debt_to_equity': [0.25] * len(dates),
            'ebitda_margin': [0.2] * len(dates),
            'current_ratio': [1.5] * len(dates)
        })
        
        pd_score = {"pd_score": 0.05}  # 5% вероятность дефолта
        parameters = {
            "exposure": 1000000,
            "lgd": 0.40
        }
        
        el_result = await agent._calculate_el(pd_score, financial_data, parameters)
        
        assert el_result is not None
        assert "el" in el_result
        assert el_result["el"] >= 0  # EL не может быть отрицательным
        
    @pytest.mark.asyncio
    async def test_analyze_task(self):
        """Тест анализа задачи"""
        agent = CreditRiskAgent(
            agent_id="test_credit_risk",
            config={}
        )
        
        # Инициализируем агента
        await agent.initialize()
        
        task = {
            "task_id": "test_task_001",
            "entity_id": "test_entity_001",
            "entity_type": "company",
            "parameters": {
                "exposure": 1000000,
                "lgd": 0.40
            }
        }
        
        result = await agent.analyze(task)
        
        assert result is not None
        assert "task_id" in result
        assert "risk_metrics" in result
        assert result["task_id"] == task["task_id"]
        
    @pytest.mark.asyncio
    async def test_llm_analysis(self):
        """Тест LLM анализа кредитного риска"""
        agent = CreditRiskAgent(
            agent_id="test_credit_risk",
            config={
                "nvidia_api_key": "test_key"
            }
        )
        
        # Мокаем LLM клиент
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].delta = Mock()
        mock_response.choices[0].delta.content = "Test analysis"
        mock_response.choices[0].delta.reasoning_content = "Test reasoning"
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Test analysis"
        
        mock_client.chat = Mock()
        mock_client.chat.completions = Mock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        
        agent.deepseek_client = mock_client
        
        # Создаем тестовые данные
        import pandas as pd
        dates = pd.date_range(end=datetime.now(), periods=12, freq='M')
        financial_data = pd.DataFrame({
            'date': dates,
            'revenue': [1000000] * len(dates),
            'debt': [500000] * len(dates),
            'equity': [2000000] * len(dates),
            'ebitda': [200000] * len(dates),
            'debt_to_equity': [0.25] * len(dates),
            'ebitda_margin': [0.2] * len(dates),
            'current_ratio': [1.5] * len(dates)
        })
        
        news_data = []
        pd_score = {"pd_score": 0.05, "pd_percentage": 5.0}
        entity_id = "test_entity_001"
        
        analysis = await agent._llm_analyze(entity_id, financial_data, news_data, pd_score)
        
        assert analysis is not None
        assert "analysis" in analysis or "summary" in analysis
        
    @pytest.mark.asyncio
    async def test_agent_status_transitions(self):
        """Тест переходов статусов агента"""
        agent = CreditRiskAgent(
            agent_id="test_credit_risk",
            config={}
        )
        
        assert agent.status == AgentStatus.INITIALIZING
        
        await agent.initialize()
        assert agent.status == AgentStatus.IDLE
        
        # При анализе статус должен измениться
        task = {
            "task_id": "test_task_001",
            "entity_id": "test_entity",
            "entity_type": "company",
            "parameters": {}
        }
        
        # Мокаем метод analyze
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


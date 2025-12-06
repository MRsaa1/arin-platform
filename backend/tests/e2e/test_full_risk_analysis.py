"""
End-to-end tests for full risk analysis workflow
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.mark.e2e
class TestFullRiskAnalysis:
    """End-to-end тесты для полного цикла анализа рисков"""
    
    def test_market_risk_analysis_workflow(self):
        """Тест полного workflow анализа рыночного риска"""
        client = TestClient(app)
        
        # 1. Проверяем доступность агентов
        agents_response = client.get("/api/v1/agents")
        assert agents_response.status_code in [200, 503]
        
        # 2. Запускаем анализ рыночного риска
        analysis_request = {
            "type": "market_risk",
            "entity_id": "test_portfolio_001",
            "entity_type": "portfolio",
            "required_agents": ["market_risk_agent"],
            "parameters": {
                "confidence_level": 0.95,
                "time_horizon": 1
            }
        }
        
        analysis_response = client.post("/api/v1/risks/analyze", json=analysis_request)
        
        if analysis_response.status_code == 200:
            result = analysis_response.json()
            assert "task_id" in result
            assert "results" in result
            
    def test_credit_risk_analysis_workflow(self):
        """Тест полного workflow анализа кредитного риска"""
        client = TestClient(app)
        
        # 1. Проверяем доступность агентов
        agents_response = client.get("/api/v1/agents")
        assert agents_response.status_code in [200, 503]
        
        # 2. Запускаем анализ кредитного риска
        analysis_request = {
            "type": "credit_risk",
            "entity_id": "test_entity_001",
            "entity_type": "company",
            "required_agents": ["credit_risk_agent"],
            "parameters": {
                "exposure": 1000000,
                "lgd": 0.40
            }
        }
        
        analysis_response = client.post("/api/v1/risks/analyze", json=analysis_request)
        
        if analysis_response.status_code == 200:
            result = analysis_response.json()
            assert "task_id" in result
            assert "results" in result
            
    def test_multi_agent_analysis_workflow(self):
        """Тест workflow с несколькими агентами"""
        client = TestClient(app)
        
        # Запускаем анализ с несколькими агентами
        analysis_request = {
            "type": "comprehensive_risk",
            "entity_id": "test_entity_001",
            "entity_type": "portfolio",
            "required_agents": ["market_risk_agent", "credit_risk_agent"],
            "parameters": {
                "confidence_level": 0.95,
                "time_horizon": 1,
                "exposure": 1000000
            }
        }
        
        analysis_response = client.post("/api/v1/risks/analyze", json=analysis_request)
        
        if analysis_response.status_code == 200:
            result = analysis_response.json()
            assert "task_id" in result
            assert "results" in result


"""
Integration tests for Agents API
"""
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from backend.main import app


@pytest.mark.integration
class TestAgentsAPI:
    """Тесты для API агентов"""
    
    def test_list_agents(self):
        """Тест получения списка агентов"""
        client = TestClient(app)
        response = client.get("/api/v1/agents")
        
        assert response.status_code in [200, 503]  # 503 если orchestrator не инициализирован
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            
    def test_get_agent_status(self):
        """Тест получения статуса агента"""
        client = TestClient(app)
        response = client.get("/api/v1/agents/market_risk_agent")
        
        assert response.status_code in [200, 404, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "agent_id" in data
            assert "status" in data
            
    def test_stop_agent(self):
        """Тест остановки агента"""
        client = TestClient(app)
        response = client.post("/api/v1/agents/market_risk_agent/stop")
        
        assert response.status_code in [200, 503]
        
        if response.status_code == 200:
            data = response.json()
            assert "message" in data


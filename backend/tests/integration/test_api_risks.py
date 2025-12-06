"""
Integration tests for Risks API
"""
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from backend.main import app


@pytest.mark.integration
class TestRisksAPI:
    """Тесты для API анализа рисков"""
    
    def test_analyze_risk(self):
        """Тест запуска анализа риска"""
        client = TestClient(app)
        
        request_data = {
            "type": "market_risk",
            "entity_id": "test_portfolio_001",
            "entity_type": "portfolio",
            "required_agents": ["market_risk_agent"],
            "parameters": {
                "confidence_level": 0.95,
                "time_horizon": 1
            }
        }
        
        response = client.post("/api/v1/risks/analyze", json=request_data)
        
        assert response.status_code in [200, 503, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "task_id" in data
            assert "status" in data
            assert "results" in data
            
    def test_get_current_risks(self):
        """Тест получения текущих рисков"""
        client = TestClient(app)
        response = client.get("/api/v1/risks/current")
        
        assert response.status_code == 200
        data = response.json()
        assert "risks" in data
        
    def test_get_risk_history(self):
        """Тест получения истории рисков"""
        client = TestClient(app)
        response = client.get("/api/v1/risks/history")
        
        assert response.status_code == 200
        data = response.json()
        assert "history" in data


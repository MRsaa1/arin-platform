"""
Basic load testing for ARIN Platform
"""
import pytest
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
import time

from backend.main import app


@pytest.mark.slow
@pytest.mark.requires_api
class TestLoad:
    """Базовые тесты нагрузки"""
    
    def test_concurrent_requests(self):
        """Тест параллельных запросов"""
        client = TestClient(app)
        
        def make_request():
            """Выполнить запрос"""
            try:
                response = client.get("/api/v1/agents")
                return response.status_code
            except Exception as e:
                return None
        
        # Выполняем 10 параллельных запросов
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]
        
        # Проверяем, что все запросы завершились
        assert len(results) == 10
        # Большинство запросов должны быть успешными (200 или 503)
        success_count = sum(1 for r in results if r in [200, 503])
        assert success_count >= 8  # 80% успешных запросов
        
    def test_sequential_requests_performance(self):
        """Тест производительности последовательных запросов"""
        client = TestClient(app)
        
        start_time = time.time()
        
        # Выполняем 20 последовательных запросов
        for _ in range(20):
            response = client.get("/api/v1/agents")
            assert response.status_code in [200, 503]
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Проверяем, что среднее время ответа разумное (< 1 секунда на запрос)
        avg_time = elapsed / 20
        assert avg_time < 1.0, f"Average response time {avg_time:.2f}s is too high"
        
    def test_health_endpoint_load(self):
        """Тест нагрузки на health endpoint"""
        client = TestClient(app)
        
        start_time = time.time()
        
        # Выполняем 50 запросов к health endpoint
        for _ in range(50):
            response = client.get("/health")
            assert response.status_code == 200
        
        end_time = time.time()
        elapsed = end_time - start_time
        
        # Health endpoint должен быть очень быстрым
        avg_time = elapsed / 50
        assert avg_time < 0.1, f"Health endpoint too slow: {avg_time:.2f}s"


"""
ARIN Platform - Load Testing Script
Нагрузочное тестирование системы
"""
import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict, Any
from datetime import datetime
import json

# Конфигурация
BASE_URL = "http://localhost:8000"
CONCURRENT_USERS = 100  # Количество одновременных пользователей
REQUESTS_PER_USER = 10  # Количество запросов на пользователя
TOTAL_REQUESTS = CONCURRENT_USERS * REQUESTS_PER_USER


class LoadTestResult:
    """Результаты нагрузочного тестирования"""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []
        self.start_time: float = 0
        self.end_time: float = 0
        
    def add_result(self, status_code: int, duration: float, endpoint: str):
        """Добавление результата"""
        self.results.append({
            "status_code": status_code,
            "duration": duration,
            "endpoint": endpoint,
            "timestamp": datetime.now().isoformat()
        })
        
    def add_error(self, error: str, endpoint: str):
        """Добавление ошибки"""
        self.errors.append({
            "error": error,
            "endpoint": endpoint,
            "timestamp": datetime.now().isoformat()
        })
        
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики"""
        if not self.results:
            return {"error": "No results"}
        
        durations = [r["duration"] for r in self.results]
        status_codes = [r["status_code"] for r in self.results]
        
        successful = sum(1 for sc in status_codes if 200 <= sc < 300)
        failed = len(status_codes) - successful
        
        return {
            "total_requests": len(self.results),
            "successful_requests": successful,
            "failed_requests": failed,
            "success_rate": successful / len(self.results) * 100,
            "total_errors": len(self.errors),
            "total_time": self.end_time - self.start_time,
            "requests_per_second": len(self.results) / (self.end_time - self.start_time),
            "durations": {
                "mean": statistics.mean(durations),
                "median": statistics.median(durations),
                "min": min(durations),
                "max": max(durations),
                "p50": statistics.median(durations),
                "p95": self._percentile(durations, 95),
                "p99": self._percentile(durations, 99)
            },
            "status_codes": {
                str(code): status_codes.count(code)
                for code in set(status_codes)
            }
        }
        
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Вычисление перцентиля"""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]


async def make_request(
    session: aiohttp.ClientSession,
    endpoint: str,
    method: str = "GET",
    data: Dict[str, Any] = None
) -> tuple:
    """Выполнение запроса"""
    url = f"{BASE_URL}{endpoint}"
    start_time = time.time()
    
    try:
        if method == "GET":
            async with session.get(url) as response:
                duration = time.time() - start_time
                return response.status, duration, endpoint
        elif method == "POST":
            async with session.post(url, json=data) as response:
                duration = time.time() - start_time
                return response.status, duration, endpoint
    except Exception as e:
        duration = time.time() - start_time
        return None, duration, endpoint, str(e)


async def user_simulation(session: aiohttp.ClientSession, user_id: int, result: LoadTestResult):
    """Симуляция пользователя"""
    endpoints = [
        ("/health", "GET"),
        ("/api/v1/agents", "GET"),
        ("/api/v1/risks/current", "GET"),
        ("/api/v1/graph/visualization", "GET"),
        ("/api/v1/performance/health", "GET"),
    ]
    
    for i in range(REQUESTS_PER_USER):
        endpoint, method = endpoints[i % len(endpoints)]
        
        try:
            status, duration, ep = await make_request(session, endpoint, method)
            if status:
                result.add_result(status, duration, ep)
            else:
                result.add_error("Request failed", ep)
        except Exception as e:
            result.add_error(str(e), endpoint)
        
        # Небольшая задержка между запросами
        await asyncio.sleep(0.1)


async def run_load_test():
    """Запуск нагрузочного тестирования"""
    print(f"Starting load test...")
    print(f"Concurrent users: {CONCURRENT_USERS}")
    print(f"Requests per user: {REQUESTS_PER_USER}")
    print(f"Total requests: {TOTAL_REQUESTS}")
    print("-" * 50)
    
    result = LoadTestResult()
    result.start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        # Создание задач для всех пользователей
        tasks = [
            user_simulation(session, i, result)
            for i in range(CONCURRENT_USERS)
        ]
        
        # Выполнение всех задач параллельно
        await asyncio.gather(*tasks)
    
    result.end_time = time.time()
    
    # Вывод результатов
    stats = result.get_statistics()
    print("\n" + "=" * 50)
    print("LOAD TEST RESULTS")
    print("=" * 50)
    print(f"Total requests: {stats['total_requests']}")
    print(f"Successful: {stats['successful_requests']}")
    print(f"Failed: {stats['failed_requests']}")
    print(f"Success rate: {stats['success_rate']:.2f}%")
    print(f"Total time: {stats['total_time']:.2f}s")
    print(f"Requests per second: {stats['requests_per_second']:.2f}")
    print("\nResponse Times:")
    print(f"  Mean: {stats['durations']['mean']*1000:.2f}ms")
    print(f"  Median: {stats['durations']['median']*1000:.2f}ms")
    print(f"  P95: {stats['durations']['p95']*1000:.2f}ms")
    print(f"  P99: {stats['durations']['p99']*1000:.2f}ms")
    print(f"  Min: {stats['durations']['min']*1000:.2f}ms")
    print(f"  Max: {stats['durations']['max']*1000:.2f}ms")
    print("\nStatus Codes:")
    for code, count in stats['status_codes'].items():
        print(f"  {code}: {count}")
    
    if result.errors:
        print(f"\nErrors: {len(result.errors)}")
        for error in result.errors[:10]:  # Первые 10 ошибок
            print(f"  {error['error']} - {error['endpoint']}")
    
    # Сохранение результатов
    with open("load_test_results.json", "w") as f:
        json.dump({
            "statistics": stats,
            "errors": result.errors[:100]  # Первые 100 ошибок
        }, f, indent=2)
    
    print("\nResults saved to load_test_results.json")
    
    return stats


if __name__ == "__main__":
    asyncio.run(run_load_test())


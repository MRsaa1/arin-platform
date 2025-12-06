"""
ARIN Platform - Stress Testing Script
Стресс-тестирование для выявления пределов системы
"""
import asyncio
import aiohttp
import time
from typing import List, Dict, Any
from datetime import datetime
import json

BASE_URL = "http://localhost:8000"


class StressTest:
    """Стресс-тестирование системы"""
    
    def __init__(self):
        self.results: List[Dict[str, Any]] = []
        
    async def test_gradual_load(
        self,
        start_users: int = 10,
        max_users: int = 500,
        step: int = 50,
        requests_per_user: int = 5
    ):
        """Постепенное увеличение нагрузки"""
        print("Starting gradual stress test...")
        print(f"Start users: {start_users}, Max users: {max_users}, Step: {step}")
        print("-" * 50)
        
        current_users = start_users
        
        while current_users <= max_users:
            print(f"\nTesting with {current_users} concurrent users...")
            
            start_time = time.time()
            successful = 0
            failed = 0
            durations = []
            
            async with aiohttp.ClientSession() as session:
                tasks = []
                for i in range(current_users):
                    for j in range(requests_per_user):
                        tasks.append(self._make_request(session, "/health"))
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, Exception):
                        failed += 1
                    else:
                        status, duration = result
                        durations.append(duration)
                        if 200 <= status < 300:
                            successful += 1
                        else:
                            failed += 1
            
            total_time = time.time() - start_time
            total_requests = current_users * requests_per_user
            
            result = {
                "users": current_users,
                "total_requests": total_requests,
                "successful": successful,
                "failed": failed,
                "success_rate": successful / total_requests * 100 if total_requests > 0 else 0,
                "total_time": total_time,
                "requests_per_second": total_requests / total_time if total_time > 0 else 0,
                "avg_duration": sum(durations) / len(durations) if durations else 0,
                "max_duration": max(durations) if durations else 0
            }
            
            self.results.append(result)
            
            print(f"  Success rate: {result['success_rate']:.2f}%")
            print(f"  Requests/sec: {result['requests_per_second']:.2f}")
            print(f"  Avg duration: {result['avg_duration']*1000:.2f}ms")
            print(f"  Max duration: {result['max_duration']*1000:.2f}ms")
            
            # Если success rate упал ниже 50%, останавливаем тест
            if result['success_rate'] < 50:
                print(f"\n⚠️  System degraded at {current_users} users (success rate < 50%)")
                break
            
            current_users += step
            await asyncio.sleep(2)  # Пауза между тестами
        
        return self.results
        
    async def test_spike_load(
        self,
        spike_users: int = 1000,
        duration_seconds: int = 60
    ):
        """Тест на резкий скачок нагрузки"""
        print(f"\nStarting spike test: {spike_users} users for {duration_seconds}s...")
        
        start_time = time.time()
        successful = 0
        failed = 0
        durations = []
        
        async with aiohttp.ClientSession() as session:
            while time.time() - start_time < duration_seconds:
                tasks = [
                    self._make_request(session, "/health")
                    for _ in range(spike_users)
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, Exception):
                        failed += 1
                    else:
                        status, duration = result
                        durations.append(duration)
                        if 200 <= status < 300:
                            successful += 1
                        else:
                            failed += 1
                
                await asyncio.sleep(0.1)
        
        total_time = time.time() - start_time
        total_requests = successful + failed
        
        return {
            "spike_users": spike_users,
            "duration": duration_seconds,
            "total_requests": total_requests,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total_requests * 100 if total_requests > 0 else 0,
            "requests_per_second": total_requests / total_time if total_time > 0 else 0,
            "avg_duration": sum(durations) / len(durations) if durations else 0
        }
        
    async def _make_request(self, session: aiohttp.ClientSession, endpoint: str):
        """Выполнение запроса"""
        url = f"{BASE_URL}{endpoint}"
        start_time = time.time()
        
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                duration = time.time() - start_time
                return response.status, duration
        except Exception as e:
            duration = time.time() - start_time
            raise Exception(f"Request failed: {e}")
            
    def save_results(self, filename: str = "stress_test_results.json"):
        """Сохранение результатов"""
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to {filename}")


async def main():
    """Основная функция"""
    test = StressTest()
    
    # Постепенное увеличение нагрузки
    gradual_results = await test.test_gradual_load(
        start_users=10,
        max_users=500,
        step=50,
        requests_per_user=5
    )
    
    # Тест на резкий скачок
    spike_result = await test.test_spike_load(
        spike_users=1000,
        duration_seconds=60
    )
    
    test.results.append({"spike_test": spike_result})
    
    # Сохранение результатов
    test.save_results()
    
    # Вывод итогов
    print("\n" + "=" * 50)
    print("STRESS TEST SUMMARY")
    print("=" * 50)
    
    if gradual_results:
        max_users = max(r["users"] for r in gradual_results)
        print(f"Maximum users handled: {max_users}")
        
        best_result = max(gradual_results, key=lambda x: x["requests_per_second"])
        print(f"Best throughput: {best_result['requests_per_second']:.2f} req/s at {best_result['users']} users")
    
    print(f"\nSpike test results:")
    print(f"  Success rate: {spike_result['success_rate']:.2f}%")
    print(f"  Requests/sec: {spike_result['requests_per_second']:.2f}")


if __name__ == "__main__":
    asyncio.run(main())


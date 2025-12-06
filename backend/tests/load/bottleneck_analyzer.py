"""
ARIN Platform - Bottleneck Analyzer
Анализ узких мест в системе
"""
import asyncio
import aiohttp
import time
from typing import Dict, Any, List
import json
from collections import defaultdict

BASE_URL = "http://localhost:8000"


class BottleneckAnalyzer:
    """Анализатор узких мест"""
    
    def __init__(self):
        self.endpoint_stats: Dict[str, List[float]] = defaultdict(list)
        self.error_stats: Dict[str, int] = defaultdict(int)
        
    async def analyze_endpoints(self, endpoints: List[str], concurrent: int = 50):
        """Анализ производительности endpoints"""
        print("Analyzing endpoints for bottlenecks...")
        print("-" * 50)
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                print(f"\nTesting {endpoint}...")
                
                tasks = [
                    self._test_endpoint(session, endpoint)
                    for _ in range(concurrent)
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                durations = []
                errors = 0
                
                for result in results:
                    if isinstance(result, Exception):
                        errors += 1
                        self.error_stats[endpoint] += 1
                    else:
                        status, duration = result
                        durations.append(duration)
                        self.endpoint_stats[endpoint].append(duration)
                
                if durations:
                    avg_duration = sum(durations) / len(durations)
                    max_duration = max(durations)
                    min_duration = min(durations)
                    
                    print(f"  Avg duration: {avg_duration*1000:.2f}ms")
                    print(f"  Min duration: {min_duration*1000:.2f}ms")
                    print(f"  Max duration: {max_duration*1000:.2f}ms")
                    print(f"  Errors: {errors}")
                    
                    # Определение узкого места
                    if avg_duration > 1.0:  # > 1 секунда
                        print(f"  ⚠️  BOTTLENECK: Average response time > 1s")
                    if errors > concurrent * 0.1:  # > 10% ошибок
                        print(f"  ⚠️  BOTTLENECK: Error rate > 10%")
                
                await asyncio.sleep(1)
        
        return self._generate_report()
        
    async def _test_endpoint(self, session: aiohttp.ClientSession, endpoint: str):
        """Тестирование endpoint"""
        url = f"{BASE_URL}{endpoint}"
        start_time = time.time()
        
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                duration = time.time() - start_time
                return response.status, duration
        except Exception as e:
            duration = time.time() - start_time
            raise Exception(f"Request failed: {e}")
            
    def _generate_report(self) -> Dict[str, Any]:
        """Генерация отчета"""
        report = {
            "bottlenecks": [],
            "slow_endpoints": [],
            "error_prone_endpoints": []
        }
        
        for endpoint, durations in self.endpoint_stats.items():
            if durations:
                avg_duration = sum(durations) / len(durations)
                p95_duration = sorted(durations)[int(len(durations) * 0.95)]
                
                # Медленные endpoints
                if avg_duration > 0.5:  # > 500ms
                    report["slow_endpoints"].append({
                        "endpoint": endpoint,
                        "avg_duration": avg_duration,
                        "p95_duration": p95_duration
                    })
                
                # Узкие места
                if avg_duration > 1.0 or p95_duration > 2.0:
                    report["bottlenecks"].append({
                        "endpoint": endpoint,
                        "avg_duration": avg_duration,
                        "p95_duration": p95_duration,
                        "issue": "High response time"
                    })
        
        # Endpoints с ошибками
        for endpoint, error_count in self.error_stats.items():
            if error_count > 0:
                report["error_prone_endpoints"].append({
                    "endpoint": endpoint,
                    "error_count": error_count
                })
        
        return report
        
    def print_report(self, report: Dict[str, Any]):
        """Вывод отчета"""
        print("\n" + "=" * 50)
        print("BOTTLENECK ANALYSIS REPORT")
        print("=" * 50)
        
        if report["bottlenecks"]:
            print("\n🚨 CRITICAL BOTTLENECKS:")
            for bottleneck in report["bottlenecks"]:
                print(f"  {bottleneck['endpoint']}")
                print(f"    Avg: {bottleneck['avg_duration']*1000:.2f}ms")
                print(f"    P95: {bottleneck['p95_duration']*1000:.2f}ms")
                print(f"    Issue: {bottleneck['issue']}")
        
        if report["slow_endpoints"]:
            print("\n⚠️  SLOW ENDPOINTS (>500ms):")
            for endpoint in report["slow_endpoints"]:
                print(f"  {endpoint['endpoint']}: {endpoint['avg_duration']*1000:.2f}ms avg")
        
        if report["error_prone_endpoints"]:
            print("\n❌ ERROR-PRONE ENDPOINTS:")
            for endpoint in report["error_prone_endpoints"]:
                print(f"  {endpoint['endpoint']}: {endpoint['error_count']} errors")
        
        if not report["bottlenecks"] and not report["slow_endpoints"]:
            print("\n✅ No significant bottlenecks detected")


async def main():
    """Основная функция"""
    analyzer = BottleneckAnalyzer()
    
    # Список endpoints для анализа
    endpoints = [
        "/health",
        "/api/v1/agents",
        "/api/v1/risks/current",
        "/api/v1/graph/visualization",
        "/api/v1/performance/health",
        "/api/v1/llm/generate",
        "/api/v1/ml/training-history"
    ]
    
    report = await analyzer.analyze_endpoints(endpoints, concurrent=50)
    analyzer.print_report(report)
    
    # Сохранение отчета
    with open("bottleneck_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\nReport saved to bottleneck_report.json")


if __name__ == "__main__":
    asyncio.run(main())


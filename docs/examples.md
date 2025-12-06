# ARIN Platform - Code Examples

## Примеры использования API

### Python

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Вход
response = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    data={"username": "analyst", "password": "password"}
)
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Анализ кредитного риска
response = requests.post(
    f"{BASE_URL}/api/v1/risks/analyze",
    headers=headers,
    json={
        "type": "credit_analysis",
        "entity_id": "AAPL",
        "entity_type": "company",
        "parameters": {
            "include_news": True,
            "include_financials": True
        }
    }
)
result = response.json()
print(f"Analysis ID: {result['task_id']}")
print(f"Status: {result['status']}")

# 3. Получение графа зависимостей
response = requests.get(
    f"{BASE_URL}/api/v1/graph/visualization",
    headers=headers,
    params={"max_nodes": 100, "include_clusters": True}
)
graph_data = response.json()
print(f"Nodes: {len(graph_data['nodes'])}")
print(f"Edges: {len(graph_data['edges'])}")

# 4. Использование LLM для анализа
response = requests.post(
    f"{BASE_URL}/api/v1/llm/generate",
    headers=headers,
    json={
        "prompt": "Analyze the credit risk for Apple Inc. based on recent financial data.",
        "system_message": "You are a financial analyst specializing in credit risk.",
        "model_preference": ["deepseek-r1", "gpt-4"]
    }
)
llm_result = response.json()
print(f"Analysis: {llm_result['content']}")
if llm_result.get('reasoning'):
    print(f"Reasoning: {llm_result['reasoning']}")

# 5. Получение метрик производительности
response = requests.get(
    f"{BASE_URL}/api/v1/performance/health",
    headers=headers
)
health = response.json()
print(f"Health Score: {health['health_score']}")
print(f"Status: {health['status']}")
```

### JavaScript/TypeScript

```typescript
const BASE_URL = 'http://localhost:8000';

// 1. Вход
async function login(username: string, password: string) {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);
  
  const response = await fetch(`${BASE_URL}/api/v1/auth/login`, {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  return data.access_token;
}

// 2. Анализ риска
async function analyzeRisk(token: string, entityId: string) {
  const response = await fetch(`${BASE_URL}/api/v1/risks/analyze`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      type: 'credit_analysis',
      entity_id: entityId,
      entity_type: 'company'
    })
  });
  
  return await response.json();
}

// 3. Получение графа
async function getGraph(token: string) {
  const response = await fetch(
    `${BASE_URL}/api/v1/graph/visualization?max_nodes=100`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  return await response.json();
}

// Использование
(async () => {
  const token = await login('analyst', 'password');
  const analysis = await analyzeRisk(token, 'AAPL');
  const graph = await getGraph(token);
  
  console.log('Analysis:', analysis);
  console.log('Graph nodes:', graph.nodes.length);
})();
```

### cURL

```bash
# 1. Вход
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=analyst&password=password" \
  | jq -r '.access_token')

# 2. Анализ риска
curl -X POST "http://localhost:8000/api/v1/risks/analyze" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "credit_analysis",
    "entity_id": "AAPL",
    "entity_type": "company"
  }'

# 3. Получение графа
curl -X GET "http://localhost:8000/api/v1/graph/visualization?max_nodes=100" \
  -H "Authorization: Bearer $TOKEN"

# 4. Получение метрик
curl -X GET "http://localhost:8000/api/v1/performance/health" \
  -H "Authorization: Bearer $TOKEN"
```

## Примеры интеграции

### Создание API ключа для интеграции

```python
# Создание API ключа (требует admin права)
response = requests.post(
    f"{BASE_URL}/api/v1/auth/api-keys",
    headers=headers,
    json={
        "name": "Integration Key",
        "permissions": ["view_risks", "analyze_risks"],
        "expires_days": 365
    }
)
api_key_data = response.json()
api_key = api_key_data["api_key"]  # Сохраните этот ключ!

# Использование API ключа
headers = {"X-API-Key": api_key}
response = requests.get(
    f"{BASE_URL}/api/v1/risks/current",
    headers=headers
)
```

### Пакетный анализ

```python
entities = ["AAPL", "MSFT", "GOOGL", "AMZN"]

for entity_id in entities:
    response = requests.post(
        f"{BASE_URL}/api/v1/risks/analyze?async_mode=true",
        headers=headers,
        json={
            "type": "credit_analysis",
            "entity_id": entity_id,
            "entity_type": "company"
        }
    )
    task_id = response.json()["results"]["celery_task_id"]
    
    # Проверка статуса
    status_response = requests.get(
        f"{BASE_URL}/api/v1/tasks/{task_id}",
        headers=headers
    )
    print(f"{entity_id}: {status_response.json()['status']}")
```

### Экспорт данных (GDPR)

```python
# Экспорт своих данных
response = requests.get(
    f"{BASE_URL}/api/v1/compliance/gdpr/export?format=json",
    headers=headers
)
user_data = response.json()["data"]

# Сохранение в файл
with open("my_data.json", "w") as f:
    json.dump(user_data, f, indent=2)
```

## Полные примеры

### Полный цикл анализа риска

```python
import requests
import time

BASE_URL = "http://localhost:8000"

# 1. Аутентификация
token = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    data={"username": "analyst", "password": "password"}
).json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Запуск комплексного анализа
response = requests.post(
    f"{BASE_URL}/api/v1/risks/analyze",
    headers=headers,
    json={
        "type": "comprehensive_analysis",
        "entity_id": "AAPL",
        "entity_type": "company"
    }
)
task_id = response.json()["task_id"]

# 3. Ожидание завершения (для синхронного режима)
# Или проверка статуса для асинхронного
while True:
    status = requests.get(
        f"{BASE_URL}/api/v1/tasks/{task_id}",
        headers=headers
    ).json()
    
    if status["status"] == "SUCCESS":
        break
    elif status["status"] == "FAILURE":
        raise Exception("Analysis failed")
    
    time.sleep(2)

# 4. Получение результатов
results = requests.get(
    f"{BASE_URL}/api/v1/risks/current?entity_id=AAPL",
    headers=headers
).json()

# 5. Анализ графа зависимостей
graph = requests.get(
    f"{BASE_URL}/api/v1/graph/visualization?node_filter=AAPL",
    headers=headers
).json()

# 6. Проверка алертов
alerts = requests.get(
    f"{BASE_URL}/api/v1/alerts?entity_id=AAPL&severity=high",
    headers=headers
).json()

print("Analysis completed!")
print(f"Risk score: {results.get('risk_score')}")
print(f"Connected entities: {len(graph.get('nodes', []))}")
print(f"High severity alerts: {len(alerts.get('alerts', []))}")
```


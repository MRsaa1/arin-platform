# ARIN Platform - Autonomous Risk Intelligence Network

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Institutional-Grade Multi-Agent System for Predictive Risk Management**

ARIN Platform - это комплексная система управления рисками на основе Agentic AI, которая использует 6 специализированных агентов для анализа кредитных, рыночных, операционных, ликвидных, регуляторных и системных рисков.

ARIN Platform - is a comprehensive risk management system based on Agentic AI, which uses 6 specialized agents to analyze credit, market, operational, liquidity, regulatory, and systemic risks.

## 🌟 Особенности

- **6 Специализированных Агентов**: Credit, Market, Operational, Liquidity, Regulatory, Systemic Risk Agents
- **Graph-Based Analysis**: Анализ взаимосвязей и каскадных эффектов через граф зависимостей
- **LLM Integration**: DeepSeek R1 (NVIDIA API) для reasoning и GPT-4 как fallback
- **ML Models**: XGBoost для кредитного риска, GNN для системного анализа
- **Real-time Monitoring**: Performance monitoring и health checks
- **Scalable Architecture**: Docker Swarm / Kubernetes ready
- **Production Ready**: Load balancing, caching, async processing

6 Specialized Agents: Credit, Market, Operational, Liquidity, Regulatory, Systemic Risk Agents
Graph-Based Analysis: Analyze relationships and cascade effects through a dependency graph
LLM Integration: DeepSeek R1 (NVIDIA API) for reasoning and GPT-4 as a fallback
ML Models: XGBoost for credit risk, GNN for system analysis
Real-time Monitoring: Performance monitoring and health checks
Scalable Architecture: Docker Swarm / Kubernetes ready
Production Ready: Load balancing, caching, async processing

## 🏗️ Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                    ARIN Platform                        │
├─────────────────────────────────────────────────────────┤
│  Orchestrator (Task Distribution & Coordination)       │
├─────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │  Credit  │  │  Market  │  │Operational│  ...      │
│  │   Risk   │  │   Risk   │  │   Risk   │            │
│  └──────────┘  └──────────┘  └──────────┘            │
├─────────────────────────────────────────────────────────┤
│  Graph Builder (Dependency Analysis & GNN)             │
├─────────────────────────────────────────────────────────┤
│  AI Engine (LLM Manager, ML Models, Training)          │
├─────────────────────────────────────────────────────────┤
│  Data Layer (PostgreSQL, TimescaleDB, Neo4j, Redis)    │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Быстрый старт

### Требования

- Python 3.10+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis
- Neo4j 5+

### Установка

1. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/MRsaa1/arin-platform.git
   cd arin-platform
   ```

2. **Создайте `.env` файл**:
   ```bash
   cp .env.example .env
   # Отредактируйте .env и добавьте ваши API ключи
   ```

3. **Запустите через Docker Compose**:
   ```bash
   docker-compose up -d
   ```

4. **Или установите локально**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn backend.main:app --reload
   ```

### API Endpoints

- `GET /health` - Health check
- `GET /api/v1/agents` - Список агентов
- `POST /api/v1/risks/analyze` - Анализ риска
- `GET /api/v1/graph/visualization` - Визуализация графа
- `GET /api/v1/performance/health` - Метрики производительности

Полная документация API: `http://localhost:8000/docs`

## 📚 Документация

### Для пользователей
- [User Guide](docs/user-guide.md) - Руководство пользователя
- [FAQ](docs/faq.md) - Часто задаваемые вопросы
- [API Reference](docs/api-reference.md) - Справочник API
- [Examples](docs/examples.md) - Примеры использования

### Для администраторов
- [Admin Guide](docs/admin-guide.md) - Руководство администратора
- [Deployment Guide](docs/deployment-guide.md) - Развертывание
- [Troubleshooting Guide](docs/troubleshooting-guide.md) - Решение проблем

### Техническая документация
- [Project Documentation](ARIN-Project-Documentation.md) - Обзор проекта
- [Technical Architecture](ARIN-Technical-Architecture.md) - Техническая архитектура
- [Implementation Plan](ARIN-Implementation-Plan.md) - План реализации
- [NVIDIA Integration](ARIN-NVIDIA-Integration.md) - Интеграция NVIDIA
- [Performance Optimization](PERFORMANCE_OPTIMIZATION.md) - Оптимизация производительности
- [Scaling and Load Testing](SCALING_AND_LOAD_TESTING.md) - Масштабирование
- [Security Implementation](backend/SECURITY_IMPLEMENTATION.md) - Безопасность
- [Compliance Implementation](backend/COMPLIANCE_IMPLEMENTATION.md) - Compliance

## 🔧 Технологический стек

- **Backend**: FastAPI, Python 3.10+
- **AI/ML**: DeepSeek R1, GPT-4, XGBoost, PyTorch Geometric
- **Databases**: PostgreSQL, TimescaleDB, Neo4j, Redis
- **Task Queue**: Celery
- **Deployment**: Docker, Kubernetes
- **Frontend**: Next.js, React, TypeScript

## 🧪 Тестирование

```bash
# Unit tests
pytest backend/tests/unit/

# Integration tests
pytest backend/tests/integration/

# Load testing
cd backend/tests/load
python load_test.py
```

## 📊 Производительность

- ✅ Response time < 500ms для стандартных запросов
- ✅ 1000+ requests/minute
- ✅ 70%+ снижение нагрузки на БД через кэширование

## 🔒 Безопасность

См. [SECURITY.md](SECURITY.md) для информации о безопасности.

**Важно**: Все секреты хранятся в переменных окружения. Никогда не коммитьте `.env` файл!

## 🤝 Вклад

Contributions welcome! Пожалуйста:
1. Fork репозиторий
2. Создайте feature branch
3. Commit изменения
4. Push в branch
5. Создайте Pull Request

## 📊 Статус проекта

✅ **Production Ready** - Проект полностью реализован и готов к развертыванию

- ✅ Все 6 агентов работают
- ✅ Graph Builder с GNN
- ✅ LLM интеграция
- ✅ ML модели
- ✅ Безопасность и Compliance
- ✅ Масштабирование
- ✅ Полная документация

См. [Project Summary](PROJECT_SUMMARY.md) для детальной информации.

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE) файл

## 👤 Автор

**Oleksii Slieptsov** (MRsaa1)
- 🌐 [SAA Alliance](https://saa-alliance.com)
- 📧 [Portfolio](https://mrsaa1.github.io/portfolio-dashboard/)
- 🔗 [GitHub](https://github.com/MRsaa1)

## 🙏 Благодарности

- NVIDIA для бесплатных API и Blueprints
- FastAPI community
- Все open-source библиотеки, используемые в проекте

---

⭐ Если проект полезен, поставьте звезду!

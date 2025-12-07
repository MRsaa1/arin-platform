"""
ARIN Platform - Main Application
Autonomous Risk Intelligence Network
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from backend.config import settings
from backend.orchestrator.orchestrator import Orchestrator
from backend.graph_builder.graph_builder import GraphBuilder
from backend.api.routes import agents, risks, graph, alerts, health, llm, ml_models, performance, tasks, auth, compliance

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Глобальные экземпляры
orchestrator = None
graph_builder_instance = None
llm_manager_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    global orchestrator, graph_builder_instance, llm_manager_instance
    
    # Startup
    logger.info("Starting ARIN Platform...")
    
    # Инициализация Cache Service
    from backend.services import cache_service
    await cache_service.initialize()
    logger.info("Cache Service initialized")
    
    # Инициализация Database Pool
    from backend.database import db_pool
    await db_pool.initialize()
    logger.info("Database Pool initialized")
    
    # Инициализация LLM Manager
    from backend.ai_engine.llm import LLMManager
    llm_manager_instance = LLMManager()
    # Установка для API routes
    import backend.api.routes.llm as llm_routes
    llm_routes.llm_manager = llm_manager_instance
    logger.info("LLM Manager initialized")
    
    # Инициализация Graph Builder
    graph_builder_instance = GraphBuilder()
    await graph_builder_instance.initialize()
    
    # Инициализация Orchestrator
    orchestrator = Orchestrator()
    await orchestrator.initialize()
    
    # Интеграция Systemic Risk Agent с Graph Builder и другими агентами
    from backend.agents.systemic_risk_agent import SystemicRiskAgent
    if "systemic_risk_agent" in orchestrator.agents:
        systemic_agent = orchestrator.agents["systemic_risk_agent"]
        if isinstance(systemic_agent, SystemicRiskAgent):
            systemic_agent.set_graph_builder(graph_builder_instance)
            systemic_agent.set_other_agents(orchestrator.agents)
            logger.info("Systemic Risk Agent integrated with Graph Builder and other agents")
    
    logger.info("ARIN Platform started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ARIN Platform...")
    if orchestrator:
        await orchestrator.shutdown()
    if graph_builder_instance:
        await graph_builder_instance.shutdown()
    
    # Закрытие сервисов
    from backend.services import cache_service
    from backend.database import db_pool
    await cache_service.shutdown()
    await db_pool.shutdown()
    
    logger.info("ARIN Platform shut down")


# Создание FastAPI приложения
app = FastAPI(
    title="ARIN Platform",
    description="""
    **Autonomous Risk Intelligence Network** - Institutional-Grade Multi-Agent System for Predictive Risk Management
    
    ## Features
    
    * **6 Specialized Risk Agents**: Credit, Market, Operational, Liquidity, Regulatory, Systemic
    * **Graph-Based Analysis**: Dependency analysis and cascade effect detection
    * **LLM Integration**: DeepSeek R1 (NVIDIA API) for reasoning, GPT-4 as fallback
    * **ML Models**: XGBoost for credit risk, GNN for systemic analysis
    * **Real-time Monitoring**: Performance monitoring and health checks
    * **Production Ready**: Docker/Kubernetes support, load balancing, caching
    
    ## Authentication
    
    Most endpoints require authentication. Use `/api/v1/auth/login` to get a JWT token.
    
    Include the token in the Authorization header: `Bearer <token>`
    
    ## Documentation
    
    * [User Guide](docs/user-guide.md)
    * [Admin Guide](docs/admin-guide.md)
    * [Deployment Guide](docs/deployment-guide.md)
    * [API Reference](docs/api-reference.md)
    """,
    version="1.0.0",
    lifespan=lifespan,
    contact={
        "name": "ARIN Platform Support",
        "email": "support@arin-platform.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.arin-platform.com",
            "description": "Production server"
        }
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],  # Frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Performance monitoring middleware
from backend.middleware.performance_middleware import PerformanceMonitoringMiddleware
app.add_middleware(PerformanceMonitoringMiddleware)

# Audit logging middleware
from backend.middleware.audit_middleware import AuditMiddleware
app.add_middleware(AuditMiddleware)

# Подключение роутеров
app.include_router(health.router, tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(compliance.router, prefix="/api/v1/compliance", tags=["compliance"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(risks.router, prefix="/api/v1/risks", tags=["risks"])
app.include_router(graph.router, prefix="/api/v1/graph", tags=["graph"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(llm.router, prefix="/api/v1/llm", tags=["llm"])
app.include_router(ml_models.router, prefix="/api/v1/ml", tags=["ml"])
app.include_router(performance.router, prefix="/api/v1/performance", tags=["performance"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "message": "ARIN Platform API",
        "version": "1.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )


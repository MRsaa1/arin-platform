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
from backend.api.routes import agents, risks, graph, alerts, health, llm, ml_models, performance, tasks

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
    description="Autonomous Risk Intelligence Network - Multi-agent system for predictive risk management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Настроить для production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Performance monitoring middleware
from backend.middleware.performance_middleware import PerformanceMonitoringMiddleware
app.add_middleware(PerformanceMonitoringMiddleware)

# Подключение роутеров
app.include_router(health.router, tags=["health"])
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


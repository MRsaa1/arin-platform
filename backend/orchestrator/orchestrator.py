"""
ARIN Platform - Orchestrator
Центральный координатор всех агентов
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from backend.config import settings
from backend.agents.base_agent import BaseAgent, AgentStatus

logger = logging.getLogger(__name__)


class Orchestrator:
    """Оркестратор для управления агентами"""
    
    def __init__(self):
        """Инициализация Orchestrator"""
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_tasks: Dict[str, asyncio.Task] = {}
        self.task_queue = asyncio.Queue()
        self._running = False
        
    async def initialize(self):
        """Инициализация Orchestrator и агентов"""
        logger.info("Initializing Orchestrator...")
        
        try:
            # Инициализация агентов согласно плану
            # Фаза 1, Месяц 2: Market Risk Agent
            from backend.agents.market_risk_agent import MarketRiskAgent
            from backend.config import settings
            
            # Создание конфигурации для агентов
            agent_config = {
                "database_url": settings.database_url,
                "risk_analyzer_url": settings.risk_analyzer_url,
                "openai_api_key": settings.openai_api_key,
                "nvidia_api_key": settings.nvidia_api_key  # Используется для DeepSeek R1
            }
            
            # Регистрация Market Risk Agent
            market_risk_agent = MarketRiskAgent(
                agent_id="market_risk_agent",
                config=agent_config
            )
            await self.register_agent(market_risk_agent)
            
            # Регистрация Credit Risk Agent (Фаза 1, Месяц 2, Неделя 7-8)
            from backend.agents.credit_risk_agent import CreditRiskAgent
            
            credit_risk_agent = CreditRiskAgent(
                agent_id="credit_risk_agent",
                config=agent_config
            )
            await self.register_agent(credit_risk_agent)
            
            # Регистрация Operational Risk Agent (Фаза 2, Месяц 4, Неделя 13-14)
            from backend.agents.operational_risk_agent import OperationalRiskAgent
            
            operational_risk_agent = OperationalRiskAgent(
                agent_id="operational_risk_agent",
                config=agent_config
            )
            await self.register_agent(operational_risk_agent)
            
            # Регистрация Liquidity Risk Agent (Фаза 2, Месяц 4, Неделя 13-14)
            from backend.agents.liquidity_risk_agent import LiquidityRiskAgent
            
            liquidity_risk_agent = LiquidityRiskAgent(
                agent_id="liquidity_risk_agent",
                config=agent_config
            )
            await self.register_agent(liquidity_risk_agent)
            
            # Регистрация Regulatory Risk Agent (Фаза 2, Месяц 4, Неделя 15-16)
            from backend.agents.regulatory_risk_agent import RegulatoryRiskAgent
            
            regulatory_risk_agent = RegulatoryRiskAgent(
                agent_id="regulatory_risk_agent",
                config=agent_config
            )
            await self.register_agent(regulatory_risk_agent)
            
            # Регистрация Systemic Risk Agent (Фаза 2, Месяц 4, Неделя 15-16)
            from backend.agents.systemic_risk_agent import SystemicRiskAgent
            
            systemic_risk_agent = SystemicRiskAgent(
                agent_id="systemic_risk_agent",
                config=agent_config
            )
            await self.register_agent(systemic_risk_agent)
            
            logger.info("Orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Orchestrator: {e}")
            raise
            
    async def register_agent(self, agent: BaseAgent):
        """
        Регистрация агента
        
        Args:
            agent: Экземпляр агента
        """
        if agent.agent_id in self.agents:
            logger.warning(f"Agent {agent.agent_id} already registered")
            return
            
        self.agents[agent.agent_id] = agent
        
        # Запуск агента в отдельной задаче
        task = asyncio.create_task(agent.run())
        self.agent_tasks[agent.agent_id] = task
        
        logger.info(f"Agent {agent.agent_name} ({agent.agent_id}) registered")
        
    async def unregister_agent(self, agent_id: str):
        """
        Отмена регистрации агента
        
        Args:
            agent_id: ID агента
        """
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found")
            return
            
        agent = self.agents[agent_id]
        await agent.stop()
        
        # Отмена задачи агента
        if agent_id in self.agent_tasks:
            self.agent_tasks[agent_id].cancel()
            try:
                await self.agent_tasks[agent_id]
            except asyncio.CancelledError:
                pass
            del self.agent_tasks[agent_id]
            
        del self.agents[agent_id]
        logger.info(f"Agent {agent_id} unregistered")
        
    async def distribute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Распределение задачи между агентами
        
        Args:
            task: Задача для обработки
            
        Returns:
            Результаты обработки
        """
        task_type = task.get("type")
        required_agents = task.get("required_agents", [])
        
        logger.info(f"Distributing task {task.get('task_id')} of type {task_type}")
        
        results = {}
        
        # Определение нужных агентов на основе типа задачи
        if not required_agents:
            # Автоматическое определение агентов
            required_agents = self._determine_required_agents(task_type)
            
        # Распределение задачи между агентами
        for agent_id in required_agents:
            if agent_id not in self.agents:
                logger.warning(f"Agent {agent_id} not found, skipping")
                continue
                
            agent = self.agents[agent_id]
            try:
                result = await agent.process_task(task)
                results[agent_id] = result
            except Exception as e:
                logger.error(f"Agent {agent_id} failed to process task: {e}")
                results[agent_id] = {"error": str(e)}
                
        # Агрегация результатов
        aggregated_result = await self._aggregate_results(results, task)
        
        return aggregated_result
        
    def _determine_required_agents(self, task_type: str) -> List[str]:
        """
        Определение нужных агентов на основе типа задачи
        
        Args:
            task_type: Тип задачи
            
        Returns:
            Список ID агентов
        """
        # Маппинг типов задач на агентов
        task_agent_mapping = {
            "credit_risk": ["credit_risk_agent"],
            "market_risk": ["market_risk_agent"],
            "operational_risk": ["operational_risk_agent"],
            "liquidity_risk": ["liquidity_risk_agent"],
            "regulatory_risk": ["regulatory_risk_agent"],
            "systemic_risk": ["systemic_risk_agent"],
            "regulatory_analysis": ["regulatory_risk_agent"],
            "systemic_analysis": ["systemic_risk_agent"],
            "comprehensive_risk": [
                "credit_risk_agent",
                "market_risk_agent",
                "operational_risk_agent",
                "liquidity_risk_agent",
                "regulatory_risk_agent",
                "systemic_risk_agent"
            ],
            "credit_analysis": ["credit_risk_agent"],
            "market_analysis": ["market_risk_agent"],
            "operational_analysis": ["operational_risk_agent"],
            "liquidity_analysis": ["liquidity_risk_agent"],
            "default_analysis": ["credit_risk_agent"]  # Анализ дефолта
        }
        
        return task_agent_mapping.get(task_type, [])
        
    async def _aggregate_results(self, results: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Агрегация результатов от разных агентов
        
        Args:
            results: Результаты от агентов
            task: Исходная задача
            
        Returns:
            Агрегированные результаты
        """
        aggregated = {
            "task_id": task.get("task_id"),
            "timestamp": datetime.now().isoformat(),
            "agent_results": results,
            "overall_status": "completed" if all(
                "error" not in r for r in results.values()
            ) else "partial_failure"
        }
        
        # Дополнительная агрегация будет добавлена позже
        # (например, расчет общего риска, каскадный анализ и т.д.)
        
        return aggregated
        
    async def get_agent_status(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Получение статуса агента(ов)
        
        Args:
            agent_id: ID агента (если None, возвращает статус всех)
            
        Returns:
            Статус агента(ов)
        """
        if agent_id:
            if agent_id not in self.agents:
                return {"error": f"Agent {agent_id} not found"}
            return self.agents[agent_id].get_status()
        else:
            return {
                agent_id: agent.get_status()
                for agent_id, agent in self.agents.items()
            }
            
    async def shutdown(self):
        """Остановка Orchestrator и всех агентов"""
        logger.info("Shutting down Orchestrator...")
        
        # Остановка всех агентов
        for agent_id, agent in list(self.agents.items()):
            await self.unregister_agent(agent_id)
            
        self._running = False
        logger.info("Orchestrator shut down")


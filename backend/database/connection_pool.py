"""
ARIN Platform - Database Connection Pool
Управление пулом соединений для оптимизации производительности
"""
import logging
from typing import Optional
from contextlib import asynccontextmanager
import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from backend.config import settings

logger = logging.getLogger(__name__)


class DatabasePool:
    """
    Менеджер пула соединений с БД
    
    Оптимизирует производительность через:
    - Connection pooling
    - Prepared statements
    - Query optimization
    """
    
    def __init__(self):
        """Инициализация Database Pool"""
        self.engine = None
        self.async_session_maker = None
        self.pool_size = 20
        self.max_overflow = 10
        
    async def initialize(self):
        """Инициализация пула соединений"""
        try:
            # Создание async engine с connection pooling
            self.engine = create_async_engine(
                settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_pre_ping=True,  # Проверка соединений перед использованием
                echo=False  # Логирование SQL запросов (False для production)
            )
            
            # Создание session maker
            self.async_session_maker = async_sessionmaker(
                self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            logger.info(
                f"Database pool initialized: "
                f"pool_size={self.pool_size}, max_overflow={self.max_overflow}"
            )
            
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
            
    @asynccontextmanager
    async def get_session(self):
        """
        Получение сессии БД из пула
        
        Usage:
            async with db_pool.get_session() as session:
                result = await session.execute(query)
        """
        if not self.async_session_maker:
            raise RuntimeError("Database pool not initialized")
            
        async with self.async_session_maker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
                
    async def execute_query(
        self,
        query: str,
        parameters: Optional[dict] = None
    ):
        """
        Выполнение запроса с использованием пула
        
        Args:
            query: SQL запрос
            parameters: Параметры запроса
            
        Returns:
            Результаты запроса
        """
        async with self.get_session() as session:
            result = await session.execute(query, parameters or {})
            return result.fetchall()
            
    async def shutdown(self):
        """Закрытие пула соединений"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database pool closed")


# Глобальный экземпляр
db_pool = DatabasePool()


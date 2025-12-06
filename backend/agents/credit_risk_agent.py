"""
ARIN Platform - Credit Risk Agent
Агент для анализа кредитного риска
"""
import logging
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

from backend.agents.base_agent import BaseAgent, AgentStatus
from backend.config import settings

logger = logging.getLogger(__name__)


class CreditRiskAgent(BaseAgent):
    """Агент для анализа кредитного риска"""
    
    def __init__(self, agent_id: str = "credit_risk_agent", config: Optional[Dict[str, Any]] = None):
        """
        Инициализация Credit Risk Agent
        
        Args:
            agent_id: ID агента
            config: Конфигурация агента
        """
        if config is None:
            config = {}
            
        super().__init__(
            agent_id=agent_id,
            agent_name="Credit Risk Agent",
            config=config
        )
        
        self.db_engine = None
        self.llm_client = None
        self.deepseek_client = None
        self.ml_model = None
        self.llm_manager = None  # Новый LLM Manager
        
    async def _setup_data_access(self):
        """Настройка доступа к данным"""
        try:
            # TODO: Настроить подключение к БД
            # from sqlalchemy import create_engine
            # self.db_engine = create_engine(settings.database_url)
            
            logger.info("Credit Risk Agent data access setup completed")
        except Exception as e:
            logger.error(f"Failed to setup data access: {e}")
            raise
            
    async def _setup_ai_integration(self):
        """Настройка AI интеграции"""
        try:
            # Инициализация LLM Manager (централизованное управление)
            from backend.ai_engine.llm import LLMManager
            self.llm_manager = LLMManager()
            logger.info("LLM Manager initialized for Credit Risk Agent")
            
            # Обратная совместимость: сохранение старых клиентов для fallback
            if self.config.get("nvidia_api_key"):
                try:
                    from openai import OpenAI
                    self.deepseek_client = OpenAI(
                        base_url="https://integrate.api.nvidia.com/v1",
                        api_key=self.config.get("nvidia_api_key")
                    )
                except Exception as e:
                    logger.warning(f"Failed to initialize DeepSeek R1 client: {e}")
                    self.deepseek_client = None
                    
            if self.config.get("openai_api_key"):
                try:
                    from openai import OpenAI
                    self.llm_client = OpenAI(api_key=self.config.get("openai_api_key"))
                except Exception as e:
                    logger.warning(f"Failed to initialize OpenAI client: {e}")
                    self.llm_client = None
            
            # Загрузка ML модели
            await self._load_ml_model()
            
            logger.info("Credit Risk Agent AI integration setup completed")
        except Exception as e:
            logger.error(f"Failed to setup AI integration: {e}")
            raise
            
    async def _load_ml_model(self):
        """Загрузка ML модели для предсказания дефолта"""
        try:
            from pathlib import Path
            from backend.ai_engine.ml_models.credit_risk_model import CreditRiskModel
            
            # Путь к модели
            model_path = Path(__file__).parent.parent / "models" / "credit_risk_model.pkl"
            
            if model_path.exists():
                model = CreditRiskModel()
                model.load(str(model_path))
                self.ml_model = model
                logger.info(f"ML model loaded from {model_path}")
            else:
                logger.info(f"ML model not found at {model_path}. Will use financial metrics method.")
                self.ml_model = None
                
        except Exception as e:
            logger.warning(f"Failed to load ML model: {e}")
            self.ml_model = None
            
    async def analyze(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Анализ кредитного риска
        
        Args:
            task: Задача для анализа
                - entity_id: ID сущности (компания, заемщик)
                - entity_type: Тип сущности
                - parameters: Дополнительные параметры
                
        Returns:
            Результаты анализа кредитного риска
        """
        entity_id = task.get("entity_id")
        entity_type = task.get("entity_type", "company")
        parameters = task.get("parameters", {})
        
        logger.info(f"Analyzing credit risk for {entity_type} {entity_id}")
        
        try:
            # 1. Получение финансовых данных
            financial_data = await self._get_financial_data(entity_id, entity_type)
            
            # 2. Получение новостей (опционально)
            news_data = await self._get_news_data(entity_id)
            
            # 3. Расчет PD (Probability of Default)
            pd_score = await self._calculate_pd(financial_data, news_data)
            
            # 4. Расчет EL (Expected Loss)
            el = await self._calculate_el(pd_score, financial_data, parameters)
            
            # 5. Анализ с помощью LLM
            llm_analysis = await self._llm_analyze(entity_id, financial_data, news_data, pd_score)
            
            # 6. Генерация рекомендаций
            recommendations = await self._generate_recommendations(
                pd_score, el, financial_data, llm_analysis
            )
            
            result = {
                "agent_id": self.agent_id,
                "agent_name": self.agent_name,
                "entity_id": entity_id,
                "entity_type": entity_type,
                "timestamp": datetime.now().isoformat(),
                "pd_score": pd_score,
                "expected_loss": el,
                "financial_metrics": self._extract_financial_metrics(financial_data),
                "llm_analysis": llm_analysis,
                "recommendations": recommendations,
                "risk_score": self._calculate_overall_risk_score(pd_score, el)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to analyze credit risk: {e}")
            raise
            
    async def _get_financial_data(
        self, 
        entity_id: Optional[str], 
        entity_type: str
    ) -> pd.DataFrame:
        """
        Получение финансовых данных
        
        Args:
            entity_id: ID сущности
            entity_type: Тип сущности
            
        Returns:
            DataFrame с финансовыми данными
        """
        # Попытка получить данные из Investment Dashboard
        if self.config.get("investment_dashboard_url"):
            try:
                from backend.integrations.investment_dashboard import InvestmentDashboardClient
                dashboard_client = InvestmentDashboardClient(
                    self.config.get("investment_dashboard_url")
                )
                
                # Получение финансовых отчетов
                income_statement = await dashboard_client.get_financial_statements(
                    ticker=entity_id,
                    statement_type="income_statement",
                    period="annual"
                )
                
                if income_statement is not None and not income_statement.empty:
                    logger.info(f"Financial data retrieved from Investment Dashboard for {entity_id}")
                    return income_statement
            except Exception as e:
                logger.warning(f"Failed to get data from Investment Dashboard: {e}")
        
        # Fallback: генерация тестовых данных
        dates = pd.date_range(end=datetime.now(), periods=12, freq='M')
        
        # Примерные финансовые метрики
        np.random.seed(42)
        revenue = 1000000 + np.random.normal(0, 100000, len(dates))
        debt = 500000 + np.random.normal(0, 50000, len(dates))
        equity = 2000000 + np.random.normal(0, 200000, len(dates))
        ebitda = revenue * 0.2 + np.random.normal(0, 20000, len(dates))
        
        data = pd.DataFrame({
            'date': dates,
            'revenue': revenue,
            'debt': debt,
            'equity': equity,
            'ebitda': ebitda,
            'debt_to_equity': debt / equity,
            'ebitda_margin': ebitda / revenue,
            'current_ratio': 1.5 + np.random.normal(0, 0.2, len(dates))
        })
        
        return data
        
    async def _get_news_data(self, entity_id: Optional[str]) -> list:
        """
        Получение новостей о компании
        
        Args:
            entity_id: ID сущности
            
        Returns:
            Список новостей
        """
        # Опциональная интеграция с News Analytics Portal
        if self.config.get("news_analytics_url"):
            try:
                from backend.integrations.news_analytics import NewsAnalyticsClient
                news_client = NewsAnalyticsClient(self.config.get("news_analytics_url"))
                news = await news_client.get_news(
                    entity_id=entity_id,
                    limit=10
                )
                return news
            except Exception as e:
                logger.warning(f"Failed to get news from News Analytics: {e}")
        
        return []
        
    async def _calculate_pd(
        self, 
        financial_data: pd.DataFrame, 
        news_data: list
    ) -> Dict[str, Any]:
        """
        Расчет PD (Probability of Default)
        
        Args:
            financial_data: Финансовые данные
            news_data: Новости о компании
            
        Returns:
            Результаты расчета PD
        """
        # Извлечение последних финансовых метрик
        latest = financial_data.iloc[-1]
        
        # Базовые финансовые метрики для расчета PD
        debt_to_equity = latest.get('debt_to_equity', 0.5)
        ebitda_margin = latest.get('ebitda_margin', 0.2)
        current_ratio = latest.get('current_ratio', 1.5)
        
        # Простая модель PD на основе финансовых метрик
        # В production это будет ML модель
        
        # Базовый PD на основе debt-to-equity
        base_pd = min(max(debt_to_equity * 0.1, 0.01), 0.5)  # 1% - 50%
        
        # Корректировка на основе EBITDA margin
        if ebitda_margin < 0.1:
            base_pd *= 1.5  # Низкая маржинальность увеличивает риск
        elif ebitda_margin > 0.3:
            base_pd *= 0.7  # Высокая маржинальность снижает риск
            
        # Корректировка на основе current ratio
        if current_ratio < 1.0:
            base_pd *= 1.3  # Низкая ликвидность увеличивает риск
        elif current_ratio > 2.0:
            base_pd *= 0.9  # Высокая ликвидность снижает риск
            
        # Использование ML модели если доступна
        ml_pd = None
        if self.ml_model is not None and hasattr(self.ml_model, 'predict_proba'):
            try:
                features = self._extract_features(financial_data, news_data)
                # Преобразование в numpy array
                import numpy as np
                features_array = np.array([features])
                ml_pd = self.ml_model.predict_proba(features_array)[0][1]
                logger.info(f"ML model prediction: PD = {ml_pd:.4f}")
            except Exception as e:
                logger.warning(f"ML model prediction failed: {e}")
        
        # Использование ML предсказания если доступно, иначе базовое
        final_pd = ml_pd if ml_pd is not None else base_pd
        
        return {
            "pd_score": float(final_pd),
            "pd_percentage": float(final_pd * 100),
            "base_pd": float(base_pd),
            "ml_pd": float(ml_pd) if ml_pd is not None else None,
            "method": "ml_model" if ml_pd is not None else "financial_metrics",
            "confidence": 0.85 if ml_pd is not None else 0.70
        }
        
    def _extract_features(
        self, 
        financial_data: pd.DataFrame, 
        news_data: list
    ) -> list:
        """
        Извлечение признаков для ML модели
        
        Args:
            financial_data: Финансовые данные
            news_data: Новости
            
        Returns:
            Список признаков
        """
        latest = financial_data.iloc[-1]
        
        features = [
            latest.get('debt_to_equity', 0.5),
            latest.get('ebitda_margin', 0.2),
            latest.get('current_ratio', 1.5),
            latest.get('revenue', 1000000) / 1000000,  # Нормализация
            latest.get('debt', 500000) / 1000000,  # Нормализация
            len(news_data),  # Количество новостей
            # TODO: Добавить больше признаков (тренды, волатильность и т.д.)
        ]
        
        return features
        
    async def _calculate_el(
        self, 
        pd_score: Dict[str, Any], 
        financial_data: pd.DataFrame,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Расчет EL (Expected Loss)
        EL = PD * LGD * EAD
        
        Args:
            pd_score: Результаты расчета PD
            financial_data: Финансовые данные
            parameters: Параметры расчета (LGD, EAD)
            
        Returns:
            Результаты расчета EL
        """
        pd = pd_score.get("pd_score", 0.05)
        
        # LGD (Loss Given Default) - потери при дефолте
        # По умолчанию 45% (среднее значение для корпоративных займов)
        lgd = parameters.get("lgd", 0.45)
        
        # EAD (Exposure at Default) - экспозиция при дефолте
        # По умолчанию берем из финансовых данных (debt)
        latest = financial_data.iloc[-1]
        ead = parameters.get("ead", latest.get('debt', 1000000))
        
        # Расчет EL
        el = pd * lgd * ead
        
        # Расчет компонентов
        return {
            "expected_loss": float(el),
            "pd": float(pd),
            "lgd": float(lgd),
            "ead": float(ead),
            "formula": "EL = PD * LGD * EAD",
            "breakdown": {
                "pd_component": float(pd * 100),
                "lgd_component": float(lgd * 100),
                "ead_component": float(ead)
            }
        }
        
    async def _llm_analyze(
        self,
        entity_id: Optional[str],
        financial_data: pd.DataFrame,
        news_data: list,
        pd_score: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Анализ с помощью LLM
        
        Использует LLM Manager с кэшированием, retry логикой и автоматическим переключением
        
        Args:
            entity_id: ID сущности
            financial_data: Финансовые данные
            news_data: Новости
            pd_score: Результаты расчета PD
            
        Returns:
            Результаты LLM анализа
        """
        if not self.llm_manager:
            return {
                "analysis": "LLM analysis not available (LLM Manager not initialized)",
                "model": None
            }
            
        try:
            # Использование специализированного промпта
            from backend.ai_engine.llm import PromptTemplates
            
            latest = financial_data.iloc[-1]
            financial_metrics = {
                "revenue": latest.get('revenue', 0),
                "debt": latest.get('debt', 0),
                "equity": latest.get('equity', 0),
                "debt_to_equity": latest.get('debt_to_equity', 0),
                "ebitda_margin": latest.get('ebitda_margin', 0),
                "current_ratio": latest.get('current_ratio', 0)
            }
            
            credit_history = {
                "news_count": len(news_data),
                "pd_score": pd_score.get('pd_percentage', 0)
            }
            
            prompt = PromptTemplates.credit_risk_analysis(
                entity_name=entity_id or "Unknown",
                financial_metrics=financial_metrics,
                credit_history=credit_history,
                pd_score=pd_score.get('pd_score', 0)
            )
            
            # Генерация через LLM Manager (с кэшированием и retry)
            response = await self.llm_manager.generate(
                prompt=prompt,
                agent_type="credit_risk",
                use_reasoning=True,  # Использовать reasoning модель (DeepSeek R1)
                use_cache=True,
                temperature=0.6,
                max_tokens=4096
            )
            
            return {
                "analysis": response.content,
                "reasoning": response.reasoning,
                "model": response.model or response.provider.value,
                "cached": response.cached,
                "tokens_used": response.tokens_used
            }
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {
                "analysis": f"LLM analysis failed: {str(e)}",
                "model": None
            }
                            reasoning_parts.append(reasoning)
                            
                        # Final content (финальный ответ)
                        if chunk.choices[0].delta.content is not None:
                            content_parts.append(chunk.choices[0].delta.content)
                    
                    reasoning_text = "".join(reasoning_parts) if reasoning_parts else None
                    analysis_text = "".join(content_parts)
                    
                    risk_assessment = self._parse_llm_response(analysis_text)
                    
                    return {
                        "analysis": analysis_text,
                        "reasoning": reasoning_text,  # Процесс рассуждения DeepSeek R1
                        "model": "deepseek-ai/deepseek-r1",
                        "risk_assessment": risk_assessment,
                        "timestamp": datetime.now().isoformat(),
                        "reasoning_quality": "high",  # DeepSeek R1 лучше для reasoning
                        "via_nvidia": True
                    }
                except Exception as e:
                    logger.warning(f"DeepSeek R1 analysis failed: {e}, falling back to GPT-4")
                    # Fallback к GPT-4
                    
            # Fallback: GPT-4
            if self.llm_client:
                response = self.llm_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Ты финансовый аналитик, специализирующийся на кредитном риске. Анализируй данные профессионально и предоставляй структурированные рекомендации."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                
                analysis_text = response.choices[0].message.content
                risk_assessment = self._parse_llm_response(analysis_text)
                
                return {
                    "analysis": analysis_text,
                    "model": "gpt-4",
                    "risk_assessment": risk_assessment,
                    "timestamp": datetime.now().isoformat(),
                    "reasoning_quality": "medium"  # GPT-4 хорош, но не специализирован на reasoning
                }
            else:
                raise Exception("No LLM client available")
            
        except Exception as e:
            logger.error(f"LLM analysis failed: {e}")
            return {
                "analysis": f"LLM analysis failed: {str(e)}",
                "model": None,
                "error": str(e)
            }
            
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """
        Парсинг ответа LLM для извлечения структурированных данных
        
        Args:
            response_text: Текст ответа от LLM
            
        Returns:
            Структурированные данные
        """
        # Простой парсинг (можно улучшить)
        risk_score = None
        
        # Попытка извлечь оценку риска
        import re
        score_match = re.search(r'(\d+)/10', response_text)
        if score_match:
            risk_score = int(score_match.group(1))
        else:
            # Альтернативный поиск
            score_match = re.search(r'риск[а]?[:\s]+(\d+)', response_text, re.IGNORECASE)
            if score_match:
                risk_score = int(score_match.group(1))
                
        return {
            "risk_score": risk_score,
            "raw_text": response_text
        }
        
    def _extract_financial_metrics(self, financial_data: pd.DataFrame) -> Dict[str, Any]:
        """
        Извлечение ключевых финансовых метрик
        
        Args:
            financial_data: Финансовые данные
            
        Returns:
            Ключевые метрики
        """
        latest = financial_data.iloc[-1]
        
        return {
            "revenue": float(latest.get('revenue', 0)),
            "debt": float(latest.get('debt', 0)),
            "equity": float(latest.get('equity', 0)),
            "debt_to_equity": float(latest.get('debt_to_equity', 0)),
            "ebitda_margin": float(latest.get('ebitda_margin', 0)),
            "current_ratio": float(latest.get('current_ratio', 0))
        }
        
    async def _generate_recommendations(
        self,
        pd_score: Dict[str, Any],
        el: Dict[str, Any],
        financial_data: pd.DataFrame,
        llm_analysis: Dict[str, Any]
    ) -> list:
        """
        Генерация рекомендаций на основе анализа
        
        Args:
            pd_score: Результаты расчета PD
            el: Результаты расчета EL
            financial_data: Финансовые данные
            llm_analysis: Результаты LLM анализа
            
        Returns:
            Список рекомендаций
        """
        recommendations = []
        
        pd_value = pd_score.get("pd_score", 0.05)
        el_value = el.get("expected_loss", 0)
        
        # Рекомендации на основе PD
        if pd_value > 0.1:  # >10%
            recommendations.append({
                "type": "warning",
                "message": f"Высокая вероятность дефолта ({pd_value:.2%}). Рекомендуется снизить кредитный лимит или потребовать дополнительное обеспечение.",
                "priority": "high"
            })
        elif pd_value > 0.05:  # >5%
            recommendations.append({
                "type": "info",
                "message": f"Умеренная вероятность дефолта ({pd_value:.2%}). Рекомендуется усилить мониторинг.",
                "priority": "medium"
            })
            
        # Рекомендации на основе EL
        if el_value > 100000:  # >$100K
            recommendations.append({
                "type": "alert",
                "message": f"Ожидаемые потери превышают допустимый уровень (${el_value:,.0f}). Требуется хеджирование или снижение экспозиции.",
                "priority": "critical"
            })
            
        # Рекомендации на основе финансовых метрик
        latest = financial_data.iloc[-1]
        debt_to_equity = latest.get('debt_to_equity', 0.5)
        
        if debt_to_equity > 1.0:
            recommendations.append({
                "type": "warning",
                "message": f"Высокое соотношение долг/капитал ({debt_to_equity:.2f}). Рекомендуется снизить долговую нагрузку.",
                "priority": "high"
            })
            
        # Добавление рекомендаций из LLM анализа
        if llm_analysis.get("risk_assessment", {}).get("risk_score"):
            risk_score = llm_analysis["risk_assessment"]["risk_score"]
            if risk_score >= 8:
                recommendations.append({
                    "type": "alert",
                    "message": f"LLM анализ указывает на критический уровень риска ({risk_score}/10). Требуется немедленное действие.",
                    "priority": "critical",
                    "source": "llm_analysis"
                })
                
        return recommendations
        
    def _calculate_overall_risk_score(
        self,
        pd_score: Dict[str, Any],
        el: Dict[str, Any]
    ) -> float:
        """
        Расчет общего скора риска (0-100)
        
        Args:
            pd_score: Результаты расчета PD
            el: Результаты расчета EL
            
        Returns:
            Общий скор риска (0-100, где 100 - максимальный риск)
        """
        pd_value = pd_score.get("pd_score", 0.05)
        
        # Нормализация EL (предполагая максимальный EL = $1M)
        el_value = el.get("expected_loss", 0)
        el_score = min((el_value / 1000000) * 50, 50)  # Максимум 50 баллов
        
        # PD score (максимум 50 баллов)
        pd_score_normalized = min(pd_value * 100, 50)
        
        overall_score = pd_score_normalized + el_score
        
        return min(overall_score, 100.0)
        
    async def _report_result(self, result: Dict[str, Any]):
        """
        Отчет о результатах анализа
        
        Args:
            result: Результаты анализа
        """
        # TODO: Сохранение результатов в БД
        # TODO: Отправка алертов при необходимости
        
        # Обновление графа зависимостей
        try:
            from backend.main import graph_builder_instance
            if graph_builder_instance:
                await graph_builder_instance.update_graph_from_risk_analysis(result)
        except Exception as e:
            logger.warning(f"Failed to update graph: {e}")
        
        logger.info(
            f"Credit Risk Agent completed analysis for {result.get('entity_id')}. "
            f"PD: {result.get('pd_score', {}).get('pd_percentage', 0):.2f}%, "
            f"Risk score: {result.get('risk_score', 0):.2f}"
        )
        
        # Генерация алертов при высоком риске
        if result.get("risk_score", 0) > 70:
            logger.warning(
                f"High credit risk detected for {result.get('entity_id')}: "
                f"PD={result.get('pd_score', {}).get('pd_percentage', 0):.2f}%, "
                f"Risk score={result.get('risk_score', 0):.2f}"
            )


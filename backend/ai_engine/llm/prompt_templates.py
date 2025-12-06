"""
ARIN Platform - LLM Prompt Templates
Специализированные шаблоны промптов для каждого типа агента
"""
from typing import Dict, Any, Optional
from datetime import datetime


class PromptTemplates:
    """Шаблоны промптов для различных типов анализа"""
    
    @staticmethod
    def credit_risk_analysis(
        entity_name: str,
        financial_metrics: Dict[str, Any],
        credit_history: Dict[str, Any],
        pd_score: float
    ) -> str:
        """
        Промпт для анализа кредитного риска
        
        Args:
            entity_name: Название компании
            financial_metrics: Финансовые метрики
            credit_history: История кредитов
            pd_score: Вероятность дефолта
            
        Returns:
            Промпт
        """
        return f"""
Проанализируй кредитный риск для компании {entity_name}.

Финансовые показатели:
{_format_dict(financial_metrics)}

История кредитов:
{_format_dict(credit_history)}

Вероятность дефолта (PD): {pd_score:.2%}

Предоставь:
1. Качественную оценку кредитного риска (высокий/средний/низкий)
2. Основные факторы, влияющие на риск
3. Потенциальные последствия дефолта
4. Приоритетные рекомендации по снижению риска

Ответ должен быть структурированным и конкретным.
"""
    
    @staticmethod
    def market_risk_analysis(
        portfolio_info: Dict[str, Any],
        var_results: Dict[str, Any],
        volatility_analysis: Dict[str, Any]
    ) -> str:
        """
        Промпт для анализа рыночного риска
        
        Args:
            portfolio_info: Информация о портфеле
            var_results: Результаты VaR/CVaR
            volatility_analysis: Анализ волатильности
            
        Returns:
            Промпт
        """
        return f"""
Проанализируй рыночный риск портфеля.

Информация о портфеле:
{_format_dict(portfolio_info)}

VaR/CVaR результаты:
{_format_dict(var_results)}

Анализ волатильности:
{_format_dict(volatility_analysis)}

Предоставь:
1. Оценку рыночного риска
2. Ключевые факторы волатильности
3. Потенциальные сценарии потерь
4. Рекомендации по хеджированию и управлению риском

Ответ должен быть структурированным и конкретным.
"""
    
    @staticmethod
    def operational_risk_analysis(
        entity_id: str,
        process_metrics: Dict[str, Any],
        vulnerabilities: Dict[str, Any]
    ) -> str:
        """
        Промпт для анализа операционного риска
        
        Args:
            entity_id: ID сущности
            process_metrics: Метрики процессов
            vulnerabilities: Выявленные уязвимости
            
        Returns:
            Промпт
        """
        return f"""
Проанализируй операционный риск для {entity_id}.

Метрики процессов:
{_format_dict(process_metrics)}

Выявленные уязвимости:
{_format_dict(vulnerabilities)}

Предоставь:
1. Оценку операционного риска
2. Приоритетные уязвимости для устранения
3. Вероятность операционных сбоев
4. Рекомендации по улучшению процессов

Ответ должен быть структурированным и конкретным.
"""
    
    @staticmethod
    def liquidity_risk_analysis(
        lcr: Dict[str, Any],
        nsfr: Dict[str, Any],
        liquidity_monitoring: Dict[str, Any]
    ) -> str:
        """
        Промпт для анализа риска ликвидности
        
        Args:
            lcr: Результаты LCR
            nsfr: Результаты NSFR
            liquidity_monitoring: Мониторинг ликвидности
            
        Returns:
            Промпт
        """
        return f"""
Проанализируй риск ликвидности.

LCR (Liquidity Coverage Ratio):
{_format_dict(lcr)}

NSFR (Net Stable Funding Ratio):
{_format_dict(nsfr)}

Мониторинг ликвидности:
{_format_dict(liquidity_monitoring)}

Предоставь:
1. Оценку риска ликвидности
2. Соответствие регуляторным требованиям
3. Потенциальные проблемы с ликвидностью
4. Рекомендации по управлению ликвидностью

Ответ должен быть структурированным и конкретным.
"""
    
    @staticmethod
    def regulatory_risk_analysis(
        compliance_scores: Dict[str, Any],
        regulatory_changes: Dict[str, Any],
        jurisdiction_analysis: Dict[str, Any]
    ) -> str:
        """
        Промпт для анализа регуляторного риска
        
        Args:
            compliance_scores: Оценки соответствия
            regulatory_changes: Изменения в регуляциях
            jurisdiction_analysis: Анализ по юрисдикциям
            
        Returns:
            Промпт
        """
        return f"""
Проанализируй регуляторный риск.

Оценки соответствия:
{_format_dict(compliance_scores)}

Изменения в регуляциях:
{_format_dict(regulatory_changes)}

Анализ по юрисдикциям:
{_format_dict(jurisdiction_analysis)}

Предоставь:
1. Оценку регуляторного риска
2. Критические области несоответствия
3. Потенциальные последствия регуляторных изменений
4. Приоритетные рекомендации по compliance

Ответ должен быть структурированным и конкретным.
"""
    
    @staticmethod
    def systemic_risk_analysis(
        agent_data: Dict[str, Any],
        cascade_effects: Dict[str, Any],
        concentration_analysis: Dict[str, Any]
    ) -> str:
        """
        Промпт для анализа системного риска
        
        Args:
            agent_data: Данные от всех агентов
            cascade_effects: Каскадные эффекты
            concentration_analysis: Анализ концентрации
            
        Returns:
            Промпт
        """
        return f"""
Проанализируй системный риск на основе данных всех агентов.

Данные от агентов:
{_format_dict(agent_data)}

Каскадные эффекты:
{_format_dict(cascade_effects)}

Анализ концентрации:
{_format_dict(concentration_analysis)}

Предоставь:
1. Оценку системного риска
2. Критические взаимосвязи между рисками
3. Потенциальные каскадные эффекты
4. Рекомендации по снижению системного риска

Ответ должен быть структурированным и конкретным.
"""
    
    @staticmethod
    def extract_financial_metrics(text: str) -> str:
        """
        Промпт для извлечения финансовых метрик из текста
        
        Args:
            text: Текст для анализа
            
        Returns:
            Промпт
        """
        return f"""
Извлеки финансовые метрики из следующего текста:

{text}

Верни JSON объект со следующими полями (если доступны):
- revenue: Выручка
- debt: Долг
- equity: Собственный капитал
- ebitda: EBITDA
- net_income: Чистая прибыль
- current_ratio: Коэффициент текущей ликвидности
- debt_to_equity: Отношение долга к капиталу

Верни только JSON, без пояснений.
"""
    
    @staticmethod
    def extract_risk_factors(text: str) -> str:
        """
        Промпт для извлечения факторов риска из текста
        
        Args:
            text: Текст для анализа
            
        Returns:
            Промпт
        """
        return f"""
Извлеки факторы риска из следующего текста:

{text}

Верни JSON массив объектов, каждый со следующими полями:
- factor: Название фактора риска
- severity: Серьезность (high/medium/low)
- category: Категория (market/credit/operational/liquidity/regulatory)
- description: Описание

Верни только JSON, без пояснений.
"""


def _format_dict(data: Dict[str, Any], indent: int = 0) -> str:
    """Форматирование словаря для промпта"""
    lines = []
    indent_str = "  " * indent
    
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{indent_str}- {key}:")
            lines.append(_format_dict(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{indent_str}- {key}: {len(value)} items")
            if value and isinstance(value[0], dict):
                for i, item in enumerate(value[:3]):  # Первые 3 элемента
                    lines.append(f"{indent_str}  [{i}]:")
                    lines.append(_format_dict(item, indent + 2))
        else:
            lines.append(f"{indent_str}- {key}: {value}")
    
    return "\n".join(lines)


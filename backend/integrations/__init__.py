"""
ARIN Platform - Integrations Package
"""
from backend.integrations.risk_analyzer import RiskAnalyzerClient
from backend.integrations.news_analytics import NewsAnalyticsClient
from backend.integrations.investment_dashboard import InvestmentDashboardClient
from backend.integrations.crypto_analytics import CryptoAnalyticsClient
from backend.integrations.external_data_sources import (
    FREDClient,
    ECBClient,
    RegulatoryDatabaseClient,
    ExternalDataSourcesManager
)

__all__ = [
    "RiskAnalyzerClient",
    "NewsAnalyticsClient",
    "InvestmentDashboardClient",
    "CryptoAnalyticsClient",
    "FREDClient",
    "ECBClient",
    "RegulatoryDatabaseClient",
    "ExternalDataSourcesManager"
]

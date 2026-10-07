"""Data Provider Interfaces.
Defines abstract base classes for MarketData, Fundamentals, Macro, and News.
Ensures zero hardcoding and allows effortless provider swapping.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import pandas as pd


class MarketDataProvider(ABC):
    """Abstract base class for stock prices and OHLCV market data."""

    @abstractmethod
    async def get_index_symbols(self, index_name: str) -> List[str]:
        """Fetch list of stock symbols belonging to an index (e.g., NIFTY 50, NIFTY 500)."""
        pass

    @abstractmethod
    async def get_historical_candles(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """Fetch OHLCV historical dataframe (columns: Open, High, Low, Close, Volume)."""
        pass

    @abstractmethod
    async def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Fetch latest price, change, volume, high, low for a symbol."""
        pass


class FundamentalDataProvider(ABC):
    """Abstract base class for financial statements, valuation, and ratios."""

    @abstractmethod
    async def get_company_profile(self, symbol: str) -> Dict[str, Any]:
        """Fetch company name, sector, industry, market cap, description."""
        pass

    @abstractmethod
    async def get_financial_metrics(self, symbol: str) -> Dict[str, Any]:
        """Fetch P/E, P/B, EV/EBITDA, ROCE, ROE, Debt/Equity, FCF, sales/profit growth."""
        pass

    @abstractmethod
    async def get_shareholding_pattern(self, symbol: str) -> Dict[str, Any]:
        """Fetch Promoter, FII, DII, Public holdings and promoter pledge percentage."""
        pass


class MacroDataProvider(ABC):
    """Abstract base class for macroeconomic indicators and commodities."""

    @abstractmethod
    async def get_macro_dashboard(self) -> Dict[str, Any]:
        """Fetch key macro snapshot: Crude, Gold, USD/INR, VIX, Repo Rate, 10Y Yields."""
        pass


class NewsProvider(ABC):
    """Abstract base class for news wires and corporate announcements."""

    @abstractmethod
    async def get_market_news(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch latest market-moving news items."""
        pass

    @abstractmethod
    async def get_stock_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch news specifically for a stock."""
        pass

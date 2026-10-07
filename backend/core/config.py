"""Platform Configuration Module.
Loads environment variables and application defaults with strict type validation.
"""
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # Application & Environment
    ENVIRONMENT: str = Field(default="development", description="development | staging | production")
    APP_NAME: str = "Indian Market Trading & Research Platform"
    API_V1_STR: str = "/api/v1"
    LOG_LEVEL: str = "INFO"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8080
    SECRET_KEY: str = "trading-platform-super-secret-key-change-in-production-123456789"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080"]

    # Database Configuration (Defaults to SQLite zero-setup mode if postgres unavailable)
    DATABASE_URL: str = Field(
        default=f"sqlite+aiosqlite:///{BASE_DIR / 'data' / 'trading_platform.db'}",
        description="Async SQLAlchemy database connection string",
    )

    # Redis Cache & Worker Queue (Defaults to in-memory cache if redis unreachable)
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    CACHE_TTL_SECONDS: int = 300

    # AI Models & Providers
    DEFAULT_LLM_PROVIDER: str = "gemini"  # gemini | openai | anthropic | openai-compatible
    DEFAULT_LLM_MODEL: str = "gemini-2.5-flash"
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_COMPATIBLE_BASE_URL: Optional[str] = None
    OPENAI_COMPATIBLE_API_KEY: Optional[str] = None

    # External APIs (Optional)
    MARKET_DATA_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None
    FINANCIAL_MODELING_PREP_API_KEY: Optional[str] = None

    # Broker Execution Settings
    EXECUTION_MODE: str = Field(default="PAPER", description="RESEARCH | PAPER | LIVE")
    LIVE_TRADING_ENABLED: bool = False

    # Broker API Keys
    ZERODHA_API_KEY: Optional[str] = None
    ZERODHA_API_SECRET: Optional[str] = None
    ZERODHA_ACCESS_TOKEN: Optional[str] = None
    ANGEL_ONE_API_KEY: Optional[str] = None
    ANGEL_ONE_CLIENT_CODE: Optional[str] = None
    ANGEL_ONE_PASSWORD: Optional[str] = None
    ANGEL_ONE_TOTP_KEY: Optional[str] = None
    DHAN_CLIENT_ID: Optional[str] = None
    DHAN_ACCESS_TOKEN: Optional[str] = None
    UPSTOX_API_KEY: Optional[str] = None
    UPSTOX_API_SECRET: Optional[str] = None

    # Risk Management Defaults
    MAX_PORTFOLIO_RISK_PER_TRADE: float = 0.01  # 1% max portfolio equity risk
    MAX_SECTOR_ALLOCATION: float = 0.25  # 25% max sector exposure
    MAX_SINGLE_STOCK_ALLOCATION: float = 0.10  # 10% max single stock
    DEFAULT_STOP_LOSS_ATR_MULTIPLE: float = 2.0
    MIN_RISK_REWARD_RATIO: float = 2.0

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()

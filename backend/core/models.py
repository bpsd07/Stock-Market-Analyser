"""SQLAlchemy models for market data, fundamentals, signals, portfolios, and decisions.
Supports both PostgreSQL and SQLite.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Index,
    JSON,
)
from sqlalchemy.orm import relationship
from backend.core.database import Base


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(30), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=True)
    exchange = Column(String(10), default="NSE", index=True)
    sector = Column(String(100), index=True, nullable=True)
    industry = Column(String(100), nullable=True)
    is_nifty50 = Column(Boolean, default=False, index=True)
    is_nifty500 = Column(Boolean, default=False, index=True)
    is_fo = Column(Boolean, default=False, index=True)
    market_cap = Column(Float, nullable=True)
    last_price = Column(Float, nullable=True)
    change_pct = Column(Float, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    candles = relationship("HistoricalCandle", back_populates="stock", cascade="all, delete-orphan")
    fundamentals = relationship("FundamentalSnapshot", back_populates="stock", uselist=False)
    signals = relationship("Signal", back_populates="stock")


class HistoricalCandle(Base):
    __tablename__ = "historical_candles"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    symbol = Column(String(30), index=True, nullable=False)
    timestamp = Column(DateTime, index=True, nullable=False)
    timeframe = Column(String(10), default="1d", index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)

    stock = relationship("Stock", back_populates="candles")

    __table_args__ = (
        Index("idx_candle_symbol_tf_time", "symbol", "timeframe", "timestamp", unique=True),
    )


class FundamentalSnapshot(Base):
    __tablename__ = "fundamental_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False, index=True)
    symbol = Column(String(30), index=True, nullable=False)
    pe_ratio = Column(Float, nullable=True)
    pb_ratio = Column(Float, nullable=True)
    ev_ebitda = Column(Float, nullable=True)
    roce = Column(Float, nullable=True)
    roe = Column(Float, nullable=True)
    debt_to_equity = Column(Float, nullable=True)
    free_cash_flow_cr = Column(Float, nullable=True)
    sales_growth_3y = Column(Float, nullable=True)
    profit_growth_3y = Column(Float, nullable=True)
    promoter_holding_pct = Column(Float, nullable=True)
    fii_holding_pct = Column(Float, nullable=True)
    dii_holding_pct = Column(Float, nullable=True)
    pledged_pct = Column(Float, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

    stock = relationship("Stock", back_populates="fundamentals")


class NewsArticle(Base):
    __tablename__ = "news_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    source = Column(String(100), index=True)
    url = Column(String(1000), unique=True, index=True)
    published_at = Column(DateTime, index=True)
    sentiment_score = Column(Float, default=0.0)  # -1.0 to +1.0
    impact_level = Column(String(20), default="MEDIUM")  # HIGH, MEDIUM, LOW
    entities = Column(JSON, default=list)  # ["RELIANCE", "RBI", "CRUDE"]
    sectors = Column(JSON, default=list)
    summary = Column(Text, nullable=True)
    source_quality_score = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class MacroIndicator(Base):
    __tablename__ = "macro_indicators"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), index=True, unique=True)  # e.g., "INDIA_CPI", "RBI_REPO_RATE", "BRENT_CRUDE"
    name = Column(String(200))
    category = Column(String(50), index=True)  # INFLATION, RATES, COMMODITIES, FX
    value = Column(Float, nullable=False)
    previous_value = Column(Float, nullable=True)
    unit = Column(String(20), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)


class Signal(Base):
    __tablename__ = "signals"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=True, index=True)
    symbol = Column(String(30), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    direction = Column(String(20), nullable=False)  # BULLISH, BEARISH, NEUTRAL, NO_TRADE
    total_score = Column(Float, nullable=False)
    confidence = Column(String(20), default="MEDIUM")  # LOW, MEDIUM, HIGH
    time_horizon = Column(String(30), default="SWING")  # INTRADAY, SWING, POSITIONAL
    expected_upside_pct = Column(Float, nullable=True)
    expected_downside_pct = Column(Float, nullable=True)
    risk_reward_ratio = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    target_1 = Column(Float, nullable=True)
    target_2 = Column(Float, nullable=True)
    invalidation_level = Column(Float, nullable=True)
    thesis = Column(Text, nullable=False)
    bear_case = Column(Text, nullable=False)  # Mandatory Bear thesis
    components_breakdown = Column(JSON, default=dict)
    catalysts = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)

    stock = relationship("Stock", back_populates="signals")
    decisions = relationship("DecisionRecord", back_populates="signal")


class DecisionRecord(Base):
    __tablename__ = "decision_records"

    id = Column(Integer, primary_key=True, index=True)
    signal_id = Column(Integer, ForeignKey("signals.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    analyst_opinions = Column(JSON, default=dict)
    raw_inputs = Column(JSON, default=dict)
    prompt_version = Column(String(50), default="v1.0")
    model_used = Column(String(100), default="gemini-2.5-flash")
    traceability_hash = Column(String(64), nullable=True)

    signal = relationship("Signal", back_populates="decisions")


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), default="Default Paper Portfolio")
    initial_capital = Column(Float, default=1000000.0)  # INR 10 Lakhs default
    cash = Column(Float, default=1000000.0)
    current_equity = Column(Float, default=1000000.0)
    mode = Column(String(20), default="PAPER")  # PAPER | LIVE
    created_at = Column(DateTime, default=datetime.utcnow)

    positions = relationship("Position", back_populates="portfolio", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="portfolio", cascade="all, delete-orphan")


class Position(Base):
    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    symbol = Column(String(30), index=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    average_buy_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=True)
    target = Column(Float, nullable=True)
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    opened_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    portfolio = relationship("Portfolio", back_populates="positions")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False, index=True)
    symbol = Column(String(30), index=True, nullable=False)
    side = Column(String(10), nullable=False)  # BUY | SELL
    order_type = Column(String(20), default="MARKET")  # MARKET | LIMIT | SL | SL-M
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=True)
    status = Column(String(20), default="FILLED")  # PENDING | FILLED | REJECTED | CANCELLED
    brokerage = Column(Float, default=0.0)
    stt = Column(Float, default=0.0)
    exchange_charges = Column(Float, default=0.0)
    gst = Column(Float, default=0.0)
    sebi_charges = Column(Float, default=0.0)
    stamp_duty = Column(Float, default=0.0)
    slippage = Column(Float, default=0.0)
    total_charges = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    portfolio = relationship("Portfolio", back_populates="orders")


class BacktestRun(Base):
    __tablename__ = "backtest_runs"

    id = Column(Integer, primary_key=True, index=True)
    strategy_name = Column(String(100), nullable=False, index=True)
    universe = Column(String(50), default="NIFTY_50")
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    initial_capital = Column(Float, default=1000000.0)
    total_return_pct = Column(Float, nullable=False)
    cagr_pct = Column(Float, nullable=True)
    sharpe_ratio = Column(Float, nullable=True)
    sortino_ratio = Column(Float, nullable=True)
    max_drawdown_pct = Column(Float, nullable=True)
    win_rate_pct = Column(Float, nullable=True)
    profit_factor = Column(Float, nullable=True)
    total_trades = Column(Integer, default=0)
    metrics_json = Column(JSON, default=dict)
    equity_curve = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

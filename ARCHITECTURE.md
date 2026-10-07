# SYSTEM ARCHITECTURE: AI-Powered Indian Market Trading & Research Platform

## 1. Architectural Philosophy
The platform is designed as an institutional-grade, multi-tier, modular intelligence and quantitative trading system. It decouples data ingestion, quantitative indicator calculation, multi-factor signal fusion, macroeconomic/geopolitical reasoning, portfolio optimization, backtesting, and execution into clean, testable, and independently scalable micro-modules.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 FRONTEND TERMINAL (Next.js 14 / TypeScript)                │
│  • Macro Dashboard      • Technical Scanner        • Stock Deep Dive        │
│  • AI Multi-Agent Chat  • Backtesting Visualizer   • Paper Trading Desk     │
│  • Signal Matrix        • Event Knowledge Graph    • System Health / Admin  │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │ REST / Streaming WebSockets
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                    API GATEWAY & ORCHESTRATION (FastAPI)                    │
│  • Auth / Rate Limiting • SSE / WebSocket Feeds   • Request Routing        │
│  • Circuit Breaker      • Structured Logging       • Health & Metrics       │
└──────┬───────────────┬───────────────┬────────────────┬───────────────┬─────┘
       │               │               │                │               │
┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐  ┌──────▼──────┐ ┌──────▼──────┐
│ Market Data │ │ Technical & │ │ Fundamental │  │ Macro & Geo │ │ News & Event│
│ Engine      │ │ Screening   │ │ Valuation   │  │ Engine      │ │ Intelligence│
│ (NSE/YF/Kite│ │ (VCP/5EMA/  │ │ (P/E, ROCE, │  │ (RBI, Crude,│ │ (NER, Graph,│
│  Fallbacks) │ │  Screeni-py)│ │  FCF, Debt) │  │  Yields, FX)│ │  Sentiment) │
└──────┬──────┘ └──────┬──────┘ └──────┬──────┘  └──────┬──────┘ └──────┬──────┘
       │               │               │                │               │
       └───────────────┼───────────────┼────────────────┼───────────────┘
                       │               │                │
┌──────────────────────▼───────────────▼────────────────▼─────────────────────┐
│                      AI ANALYST MESH (14 Specialized Agents)                │
│  • Macro Analyst     • Geopolitical Analyst   • Policy Analyst              │
│  • Fundamentalist    • Technical Analyst      • Momentum Analyst            │
│  • Options Analyst   • Institutional Flow     • Earnings Analyst            │
│  • Event-Driven      • Quant Analyst          • Risk Analyst                │
│  • Mandatory Bear Analyst (Adversarial Thesis Challenger)                  │
│  • Chief Investment Analyst / Portfolio Manager (Synthesis)                │
└──────────────────────────────────────┬──────────────────────────────────────┘
                                       │
┌──────────────────────────────────────▼──────────────────────────────────────┐
│                    SIGNAL FUSION & DECISION ENGINE                          │
│  • Multi-Factor Weighting Framework (Technical, Momentum, Fundamental, etc.)│
│  • Explicit NO-TRADE Engine (Edge, Regime, Liquidity & Volatility Filters)  │
│  • Causal Chain Validation: Event ──► Macro ──► Sector ──► Company ──► Trade│
└──────────────────┬───────────────────────────────────┬──────────────────────┘
                   │                                   │
┌──────────────────▼──────────────────┐ ┌──────────────▼──────────────────────┐
│     PORTFOLIO & RISK ENGINE         │ │     BACKTESTING & WALK-FORWARD     │
│  • Kelly / ATR / Fractional Sizing  │ │  • Indian Transaction Costs (STT,  │
│  • Sector & Single-Stock Limits     │ │    GST, Stamp Duty, Slippage)      │
│  • VaR, Beta, Drawdown Guardrails   │ │  • Survivorship & Lookahead Shields │
└──────────────────┬──────────────────┘ └─────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────────────────────┐
│                   EXECUTION LAYER (Pluggable BrokerAdapter)                 │
│  • Paper Trading Simulator (Default: Slippage, Partial Fills, Order Book)  │
│  • Live Broker Adapters: Zerodha Kite, Angel One, Upstox, Dhan, Fyers       │
│  • Strict Safety: Confirmation Modal, Risk Limits, LIVE_TRADING_ENABLED=false│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Core Service Boundaries

### 2.1 Backend Architecture (`backend/`)
- **`api/`**: FastAPI endpoints organized by domain:
  - `/api/v1/market`: Live indices, market breadth, FII/DII institutional activity.
  - `/api/v1/scanner`: Screeni-py inspired technical & fundamental screening runs.
  - `/api/v1/stocks/{symbol}`: Deep-dive 360-degree analytics (technicals, fundamentals, options, filings).
  - `/api/v1/macro`: Global and Indian macroeconomic dashboard, regime classification.
  - `/api/v1/news`: Deduplicated, entity-extracted news stream and event knowledge graph.
  - `/api/v1/agents`: Multi-agent research queries, analyst consensus, and Bear Analyst challenges.
  - `/api/v1/signals`: Fused multi-factor signals with confidence scores and invalidation levels.
  - `/api/v1/backtest`: Historical and walk-forward strategy simulations.
  - `/api/v1/portfolio`: Portfolio health, factor exposure, VaR, and risk diagnostics.
  - `/api/v1/paper`: Virtual account order placement, positions, equity curve, P&L.
  - `/api/v1/system`: Observability, data freshness, rate limits, and health checks.
- **`core/`**: Shared configuration, database engine (SQLAlchemy async + SQLite zero-config fallback), Redis caching abstractions, and error handlers.
- **`data/`**: `MarketDataProvider`, `FundamentalDataProvider`, `MacroDataProvider`, `NewsProvider`, with automatic fallback cascades (Primary -> Secondary -> Cached -> Stale warning).
- **`indicators/`**: Pure-Python / NumPy / Pandas vectorized indicator calculations (RSI, MACD, EMA, SMA, ATR, ADX, Bollinger Bands, Supertrend, VWAP).
- **`screening/`**: Screeni-py technical strategies (VCP, 5 EMA, NR4/NR7, VSA, breakouts) adapted for high-throughput async processing.
- **`agents/`**: 14 specialized AI analyst agents orchestrated via clean tool-calling contracts.
- **`signals/`**: Multi-factor signal fusion model and NO-TRADE evaluation engine.
- **`backtesting/`**: Event-driven backtester with Indian statutory costs (STT, GST, Exchange charges, SEBI fees, Stamp Duty, Slippage).
- **`portfolio/`**: Position sizing algorithms (Fixed Fractional, ATR, Kelly with constraints) and risk monitoring.
- **`execution/`**: `BrokerAdapter` abstract base class with `PaperTradingBroker` and broker connectors (Kite, Angel One, etc.).

---

## 3. Data Flow & Causal Chain Architecture

The system models macroeconomic and market developments as an explicit, traceable causal chain:

```
[GEOPOLITICAL / MACRO EVENT]
         │ (e.g., Middle East Escalation / OPEC Production Cut)
         ▼
[COMMODITY / FX / RATES IMPACT]
         │ (e.g., Brent Crude jumps to $92/bbl, USD/INR depreciates to 84.50)
         ▼
[SECTOR IMPACT]
         │ (e.g., Oil Marketing Companies margin compression, Paints/Tyres input cost rise)
         ▼
[COMPANY FUNDAMENTALS]
         │ (e.g., Asian Paints Q3 EBITDA margin forecast lowered by 180 bps)
         ▼
[EXPECTED MARKET RESPONSE]
         │ (e.g., Selloff in paint equities, institutional rotation into upstream ONGC/Oil India)
         ▼
[TECHNICAL CONFIRMATION]
         │ (e.g., ONGC breaks out of 50-day base with 3.2x average volume; Asian Paints breaks 200 EMA)
         ▼
[AI MULTI-AGENT SYNTHESIS]
         │ (Bull thesis formulated; Bear Analyst checks input cost pass-through & government subsidy)
         ▼
[SIGNAL FUSION & NO-TRADE VERIFICATION]
         │ (Passes liquidity, spread, risk/reward >= 1:2.5, regime compatibility)
         ▼
[RISK-ADJUSTED POSITION SIZING & TRADE PLAN]
         │ (Entry, Stop Loss, Target 1, Target 2, Max Risk <= 1% Portfolio Equity)
         ▼
[PAPER TRADING / BROKER EXECUTION]
```

---

## 4. Multi-Agent AI System Topology

| Agent Name | Primary Specialty | Key Data Inputs | Output Deliverable |
| :--- | :--- | :--- | :--- |
| **Macro Analyst** | Global & India macro trends | RBI policy, Fed rates, inflation (CPI/WPI), GDP, PMI | Macro Regime & systemic tailwinds/headwinds |
| **Geopolitical Analyst** | Global conflicts, sanctions, tariffs | News wires, trade policy, shipping lane indices | Geopolitical shock assessment & commodity propagation |
| **India Policy Analyst** | Union Budget, PLI schemes, regulations | Gazette notifications, SEBI/RBI circulars | Policy winners & regulatory headwind identification |
| **Fundamental Analyst** | Balance sheet & valuation rigor | Quarterly results, ROCE, ROE, FCF, Debt-to-Equity | Intrinsic value estimate, margin health, balance sheet safety |
| **Technical Analyst** | Multi-timeframe trend & support/resistance | Daily/Weekly OHLCV, Moving averages, ATR, Breakouts | Technical structure, pivot levels, trend health |
| **Momentum Analyst** | Relative strength & breakout velocity | RS vs NIFTY 50, Volume spikes, 52W highs | Momentum score, volume expansion confirmation |
| **Options Analyst** | Derivatives positioning & sentiment | Futures OI, Put-Call Ratio (PCR), Max Pain, IV Rank | Options sentiment, gamma traps, dealer positioning |
| **Institutional Flow Analyst** | FII & DII smart money tracking | Daily cash market flows, block deals, bulk deals | Institutional accumulation/distribution score |
| **Earnings Analyst** | Results analysis & guidance revision | Earnings surprises, revenue growth, conference calls | Earnings acceleration & guidance quality |
| **Event-Driven Analyst** | Corporate actions & special situations | Order wins, M&A, demergers, buybacks, promoter buys | Event catalyst magnitude & timeline |
| **Quant Analyst** | Statistical edge & probabilistic modeling | Volatility distributions, historical analogues | Win probability, expected return, Sharpe estimate |
| **Risk Analyst** | Exposure limits & downside stress testing | Portfolio correlation, Beta, sector limits | Max allowable position size, drawdown risk score |
| **Bear Analyst** *(Mandatory)* | Adversarial thesis destruction | All bull hypotheses, industry headwinds, valuation | The counter-thesis, thesis invalidation price, failure triggers |
| **Chief Investment Analyst** | Synthesis & executive trade plan | All 13 analyst reports + Bear argument | Final decision (BUY/SELL/AVOID/NO-TRADE) with explainability |

---

## 5. Indian Market Transaction Cost Model (Statutory Compliance)

Any backtest or simulated trade executes using real-world Indian regulatory fee structures:
1. **STT (Securities Transaction Tax)**: 0.1% on Buy & Sell for Equity Delivery; 0.025% on Sell for Equity Intraday; 0.125% on Options Sell on intrinsic value.
2. **Exchange Turnover Charges**: NSE ~0.00297%, BSE ~0.00375%.
3. **GST (Goods & Services Tax)**: 18% on (Brokerage + Exchange Charges + SEBI Charges).
4. **SEBI Turnover Charges**: ₹10 per crore (0.0001%).
5. **Stamp Duty**: 0.015% on Buy (Delivery), 0.003% on Buy (Intraday).
6. **Slippage Model**: Variable based on average 30-day volume and bid-ask spread (default: 0.05% for large-cap, 0.15% for mid-cap, 0.30% for small-cap).

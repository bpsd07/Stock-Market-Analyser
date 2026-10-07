# ARCHITECTURE AUDIT: Screeni-py Analysis & Platform Evolution

## Executive Summary
This document provides a comprehensive architectural and engineering audit of [Screeni-py](https://github.com/pranjal-joshi/Screeni-py) (v3.0.2), evaluating its core strengths, architectural bottlenecks, technical debt, and reusable components. It outlines the strategic roadmap for transforming the foundation into a production-grade, AI-powered Indian Market Trading, Intelligence & Quantitative Research Platform.

---

## 1. System Inventory & Specifications

| Component | Screeni-py Implementation | Status in Target Platform |
| :--- | :--- | :--- |
| **Language & Runtime** | Python 3.13 / uv package manager | Python 3.12+ (tested with 3.12.4 on Windows 11) |
| **Frontend** | Streamlit (`streamlit_app.py`, ~45KB single file) | Modern Next.js 14+ / React Financial Terminal with Tailwind & WebSockets |
| **Backend / API** | CLI runner (`screenipy.py`) + Streamlit direct execution | Modular FastAPI Async API Gateway + WebSocket Streaming Engine |
| **Database** | SQLite (`Database.py`, JSON blobs) & legacy Pickles | PostgreSQL / TimescaleDB with async SQLAlchemy + SQLite local zero-config mode |
| **Vector Database** | ChromaDB (`chromadb_store`, OHLC vector embeddings) | Vector RAG Engine (pgvector / ChromaDB) for news, transcripts, filings & macro events |
| **Data Fetching** | `yfinance` + NSE CSV archives + `nsetools` | Pluggable `MarketDataProvider` (NSE Archives, Yahoo Finance, Kite, Google Finance, Mock/Offline) |
| **Technical Analysis** | `talib` with `pandas_ta_remake` fallback | Vectorized pure-Python / NumPy / Pandas TA engine + Screeni-py technical strategies |
| **Multiprocessing** | `multiprocessing.Process` queue consumers | Async worker queues + batch processing + CPU-efficient vectorization |
| **AI Agents** | `openai-agents` SDK + custom monkeypatching | Pluggable Multi-Agent AI Analyst Mesh (OpenAI, Anthropic, Gemini, Local) |
| **Broker Interface** | Kite MCP experimental streaming | Clean `BrokerAdapter` interface: Paper Trading (default) & Zerodha/Angel/Dhan/Upstox adapters |

---

## 2. In-Depth Component Analysis

### 2.1 Fetcher & Data Pipeline (`classes/Fetcher.py`)
- **Strengths**:
  - Direct scraping of official NSE India index lists via `archives.nseindia.com` (`EQUITY_L.csv`, Nifty 50, Next 50, 100, 200, 500, Midcap, Smallcap).
  - Clean mapping of Yahoo Finance symbols for Indian equities (`.NS` suffix).
  - Basic backtest date calculation utilities.
- **Weaknesses**:
  - Tight coupling to `yfinance`; lacks fallback providers, exponential backoff, circuit breaking, or corporate action adjustment validation.
  - Interactive CLI prompts (`input()`) and terminal print statements embedded directly in data fetching logic.
  - No handling of fundamental data, options open interest (OI), FII/DII institutional flows, or macroeconomic feeds.

### 2.2 Technical Analysis & Pattern Recognition (`classes/ScreenipyTA.py`, `CandlePatterns.py`, `Screener.py`)
- **Strengths**:
  - Rich collection of Indian equity technical strategies:
    - **VCP (Volatility Contraction Pattern)**: Multi-stage contraction detection using local extrema (`argrelextrema`).
    - **5 EMA Strategy**: Subashish Pani style 5-EMA mean reversion setup for Nifty and Bank Nifty with SL and Target calculation.
    - **Volume Spread Analysis (VSA)**: Supply Drought and Demand Rise candle/volume spread validations.
    - **Moving Average Confluence & Reversals**: 50/200 SMA/EMA support, resistance, and crossovers.
    - **Narrow Range Bars**: NR4 and NR7 contraction setups.
    - **18 Classic Candlestick Patterns**: Morning Star, Evening Star, 3 White Soldiers, 3 Black Crows, Hammer, Engulfing, etc.
- **Weaknesses**:
  - Reliance on C-based `ta-lib` which frequently fails compilation on Windows without specialized wheels.
  - Mixes presentation logic (ANSI color escape codes `colorText.GREEN`) directly into dataframes and return dictionaries.
  - Some pattern methods contain unhandled index errors or `traceback.print_exc()` without robust exception contracts.

### 2.3 Parallel Processing (`classes/ParallelProcessing.py`)
- **Strengths**:
  - Queue-based multiprocessing architecture for batch screening across hundreds of stocks.
- **Weaknesses**:
  - Windows-specific quirks handled with legacy PyInstaller workarounds.
  - Shared memory managed via global objects; not suitable for web service worker concurrency.
  - In `screener_tools.py`, parallel processing was abandoned in favor of a serial loop hard-capped at 50 symbols (`[:50]`) to avoid agent timeout.

### 2.4 Database & Persistence (`classes/Database.py`)
- **Strengths**:
  - Transitioned from `.pkl` pickle files to SQLite (`screenipy.db`).
  - Tables for `scan_results`, `stock_cache`, and `watchlist`.
- **Weaknesses**:
  - Stores scan results as raw unindexed JSON strings (`results_json`).
  - Lacks relational entities for fundamental metrics, trades, orders, portfolio allocations, backtest performance metrics, news articles, and AI decision audits.

### 2.5 AI Agent System (`src/agents/`)
- **Strengths**:
  - Persona YAML system (`momentum_analyst.yaml`, `swing_trader.yaml`, `value_screener.yaml`, `option_buyer.yaml`, `day_trader.yaml`).
  - Integration of APScheduler for automated cron scanning and Kite heartbeat checking.
- **Weaknesses**:
  - Severe namespace collision: the project's folder `src/agents/` shadows the external `openai-agents` package (`import agents`), necessitating runtime `sys.modules.pop()` hackery.
  - Limited toolset (only technical indicators and stock lists); lacks access to fundamental valuation, macro data, options chains, news sentiment, and risk constraints.
  - No adversarial reasoning (missing the mandatory Bear Analyst).
  - No signal fusion or explainability scoring framework.

---

## 3. Keep, Extend, Replace, Remove Matrix

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SCREENI-PY AUDIT MATRIX                         │
└────────────────────────────────────────────────────────────────────────┘
  ├── KEEP (Preserve Core Logic)
  │    ├── NSE Official Index & Symbol Extraction URLs & CSV Parsers
  │    ├── Indian Market Technical Strategies (VCP, 5-EMA, NR4/NR7, VSA)
  │    ├── 18 Classic Candlestick Patterns Pattern Matrix
  │    ├── Persona Configuration Schema (YAML-based role definitions)
  │    └── Multi-timeframe lookback calculations (daily, weekly, intraday)
  │
  ├── EXTEND (Refactor, Modernize & Modularize)
  │    ├── Pure-Python / NumPy Technical Indicators (Remove C-TA-Lib dependency)
  │    ├── Pluggable Data Provider Architecture (Yahoo + NSE + Kite + Google)
  │    ├── Screeni-py Screener Rules into Modular "Strategy as Skill" Files
  │    ├── Persistent Database into SQLAlchemy Async (Postgres + SQLite fallback)
  │    └── Kite MCP into Pluggable BrokerAdapter Interface (Paper + Live)
  │
  ├── REPLACE (Insufficient for Institutional Platform)
  │    ├── Streamlit UI  ──► Next.js 14+ Professional Financial Terminal
  │    ├── Monolithic CLI Loop ──► FastAPI Async Gateway + WebSocket Feeds
  │    ├── Serial 50-Stock Screener ──► High-performance Async Screener
  │    ├── Single-Indicator Signals ──► Multi-Factor Signal Fusion Engine
  │    └── Hardcoded LLM Prompts ──► 14-Agent Collaborative AI Mesh
  │
  └── REMOVE (Eliminate Technical Debt)
       ├── PyInstaller / OTA updater legacy code (OtaUpdater.py, spec files)
       ├── ANSI Terminal Color formatting inside data manipulation methods
       ├── sys.modules namespace hacking for openai-agents
       ├── Hardcoded time.sleep() and blocking CLI input() calls
       └── Raw pickle file persistence artifacts
```

---

## 4. Hardware & Development Environment Considerations

- **Target Development Machine**: Windows 11, AMD Ryzen 5 7th Gen (6 cores / 12 threads), 16 GB RAM, Integrated GPU (~512MB VRAM), 512 GB SSD.
- **Engineering Guardrails**:
  1. **Zero Heavy Local Deep Learning Dependencies**: Avoid downloading multi-gigabyte PyTorch/HuggingFace checkpoints or CUDA-dependent weights that overwhelm 16 GB RAM / 512 MB VRAM.
  2. **Remote LLM Inference & Lightweight Classical ML**: Use API-based reasoning (Gemini, OpenAI, Anthropic, Groq) with intelligent tiered routing and caching. Use scikit-learn / LightGBM for quantitative models.
  3. **Dual Database Capability**: Full PostgreSQL + TimescaleDB support via Docker/remote, with zero-setup SQLite fallback for instant local execution without Docker.
  4. **Async & Memory Bound Architecture**: Streaming chunk-based responses, connection pooling, and Redis/in-memory LRU caching to maintain low RAM footprint (< 1.5 GB total running stack).

---

## 5. Next Steps
1. Establish the clean, modular multi-service directory structure.
2. Formulate `ARCHITECTURE.md` specifying data flows, service boundaries, and schemas.
3. Configure environment settings (`.env.example`).
4. Build Priority 2: Core Market Data & Database Infrastructure.

# AI-Powered Indian Market Trading & Research Platform

> **An institutional-grade, multi-factor market intelligence, quantitative screening, signal fusion, portfolio analytics, backtesting, and paper-trading platform architected for the Indian equity and derivatives markets (NSE/BSE).**

---

## 🚀 Key Platform Features

1. **Screeni-py Integration & Evolution**:
   - Reusable official NSE constituent download infrastructure.
   - Preserves high-value Indian market technical strategies: **VCP (Volatility Contraction Pattern)**, **5-EMA Reversals**, **Volume Spread Analysis (Supply Drought & Demand Rise)**, **NR4/NR7**, and **18 classic candlestick patterns**.
   - Replaced fragile serial loops and C-TA-Lib dependencies with **vectorized pure-Python / NumPy calculations** and high-concurrency async scanners.

2. **14 Specialized AI Analyst Agents + Mandatory Bear Analyst**:
   - Macro, Geopolitical, Policy, Fundamental, Technical, Momentum, Options, Institutional Flow, Earnings, Event-Driven, Quant, Risk, Bear, and Chief Investment Analysts.
   - **Mandatory Adversarial Bear Analyst**: Every bullish thesis is aggressively challenged with explicit risks and invalidation triggers.

3. **Causal Macro & Geopolitical Transmission Engine**:
   - Models economic shocks: `EVENT ──► MACRO ──► COMMODITIES/FX ──► SECTOR ──► COMPANY ──► FUNDAMENTAL IMPACT ──► TECHNICAL CONFIRMATION ──► TRADE THESIS`.

4. **Multi-Factor Signal Fusion & Mandatory NO-TRADE Engine**:
   - Weighted scoring (Technical, Momentum, Fundamental, Valuation, Macro, Risk).
   - Aborts trades and explicitly issues `NO_TRADE` whenever edge is small, data is corrupt, or systemic volatility (India VIX > 28) creates unquantifiable risk.

5. **Realistic Indian Statutory Backtester**:
   - Deducts all statutory exchange tariffs: **STT (0.1%)**, **NSE turnover charges**, **SEBI charges (₹10/cr)**, **GST (18%)**, **Stamp Duty (0.015%)**, **Brokerage**, and **Slippage**.
   - Next-bar open execution to prevent look-ahead bias; benchmark comparison against NIFTY 50 Buy & Hold.

6. **Paper Trading First Execution Desk**:
   - Default safe execution mode with virtual ₹10,00,000 cash balance.
   - Live broker connections require explicit two-factor acknowledgment.

7. **Professional Financial Terminal UI**:
   - Built with Next.js 14+, TypeScript, Tailwind CSS. Dark terminal aesthetic, live macro tickers, interactive screener, deep-dive analytics, and paper trading desk.

---

## 🛠️ Quick Start (Local Development)

### 1. Prerequisites
- Python 3.12+ (tested on Windows 11)
- Node.js v20+ / npm

### 2. Backend Setup
```powershell
# In project root (e:\Trading):
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Run automated tests
pytest -v

# Start FastAPI backend (port 8000)
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup
```powershell
cd frontend
npm install
npm run dev
```
Open **[http://localhost:3000](http://localhost:3000)** for the Financial Terminal and **[http://localhost:8000/docs](http://localhost:8000/docs)** for interactive OpenAPI docs.

---

## 📚 Documentation Index
- [ARCHITECTURE_AUDIT.md](ARCHITECTURE_AUDIT.md): Deep audit of Screeni-py (KEEP, EXTEND, REPLACE, REMOVE analysis).
- [ARCHITECTURE.md](ARCHITECTURE.md): System architecture, micro-service boundaries, and data flows.
- [API_SETUP.md](API_SETUP.md): External API credentials guide and protocol.
- [DATA_SOURCES.md](DATA_SOURCES.md): Data classifications and ingestion pipelines.
- [DATABASE.md](DATABASE.md): Relational schemas, SQLite/PostgreSQL dual-mode, and decision audit logs.
- [AI_AGENTS.md](AI_AGENTS.md): The 14 AI Analyst agents and the Bear Analyst protocol.
- [BACKTESTING.md](BACKTESTING.md): Quantitative walk-forward simulator and statutory Indian tax model.
- [PAPER_TRADING.md](PAPER_TRADING.md): Paper trading engine and order book.
- [BROKER_SETUP.md](BROKER_SETUP.md): Live broker adapters (Zerodha, Angel One, Upstox, Dhan).
- [SECURITY.md](SECURITY.md): Security safeguards and credential protection.
- [DEPLOYMENT.md](DEPLOYMENT.md): Local and Docker production operations.
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md): Diagnostic runbook.

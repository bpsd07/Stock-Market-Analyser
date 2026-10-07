# Market Data Sources & Ingestion Architecture

## 1. Data Classification Hierarchy
The platform strictly classifies all ingested information into five transparent tiers:

| Tier | Classification | Description | Traceability Requirement |
| :--- | :--- | :--- | :--- |
| **Tier 1** | `PUBLIC_DATA` | Free regulatory filings, NSE/BSE official archives, public financial statements. | URL and publication timestamp stored. |
| **Tier 2** | `LICENSED_DATA` | Commercial market feeds (TrueData, GlobalDataFeeds, AlphaVantage). | Provider license & feed timestamp recorded. |
| **Tier 3** | `USER_PROVIDED_DATA` | Private broker session tokens, custom watchlists, portfolio trade logs. | Sandboxed per user session; never leaked. |
| **Tier 4** | `DERIVED_DATA` | Mathematical indicators, volatility surfaces, ATR, fused signal scores. | Fully reproducible from raw Tier 1/2 inputs. |
| **Tier 5** | `MODEL_INFERENCE` | AI Multi-Agent deliberations, Bear Analyst critique, trade plans. | Full prompt, model version, and reasoning logged. |

---

## 2. Ingestion Pipelines

### 2.1 Official NSE India Index Consistently Feeds
- **Source**: `https://archives.nseindia.com/content/indices/`
- **Universes Tracked**:
  - `ind_nifty50list.csv`: NIFTY 50 Bluechip index
  - `ind_niftynext50list.csv`: NIFTY Next 50
  - `ind_nifty100list.csv`: NIFTY 100 Large-cap benchmark
  - `ind_nifty200list.csv`: NIFTY 200 Large & Mid-cap
  - `ind_nifty500list.csv`: NIFTY 500 Broad market index
  - `ind_niftymidcap150list.csv`: NIFTY Midcap 150
  - `ind_niftysmallcap250list.csv`: NIFTY Smallcap 250
  - `EQUITY_L.csv`: Complete NSE Listed Equity universe (~2,200 securities)
- **Update Frequency**: Daily cache refresh with 24-hour TTL.

### 2.2 Historical & Intraday Candles
- **Primary Source**: Yahoo Finance via `yfinance` (`.NS` ticker symbol format).
- **Secondary Source**: Pluggable Broker Connectors (Zerodha Kite historical candles).
- **Timeframes**: `1d` (Daily for swing/positional), `1wk` (Weekly for multi-year stage analysis), `1h`/`15m` (Intraday where available).
- **Quality Checks**: Automatic bad tick rejection, volume zero spike detection, forward-split adjustment validation.

### 2.3 Macroeconomic & Global Benchmark Feeds
- **Commodities**: Brent Crude (`BZ=F`), WTI Crude (`CL=F`), Gold (`GC=F`).
- **Forex**: USD/INR Spot (`INR=X`), Dollar Index (`DX-Y.NYB`).
- **Interest Rates**: India 10Y G-Sec Yield, US 10Y Treasury Yield (`^TNX`), RBI Repo Rate.
- **Global Equities**: S&P 500 (`^GSPC`), Nasdaq (`^IXIC`), Nikkei 225 (`^N225`), Hang Seng (`^HSI`).

### 2.4 Corporate Actions & Fundamentals
- P/E, P/B, EV/EBITDA, ROCE, ROE, Free Cash Flow, Debt/Equity, Promoter Holdings, Institutional Holdings.

# Quantitative Backtesting & Walk-Forward Engine

## 1. Statutory Indian Friction Model
Most open-source backtesters report distorted profits because they omit Indian securities taxes and exchange turnover tariffs. Our engine strictly deducts all statutory costs:

1. **STT (Securities Transaction Tax)**: 0.1% on Buy & 0.1% on Sell for Equity Delivery (0.025% on sell for intraday).
2. **Exchange Turnover Charges**: 0.00297% (NSE).
3. **SEBI Turnover Charges**: ₹10 per crore (0.0001%).
4. **GST**: 18% on (Brokerage + Exchange turnover + SEBI turnover).
5. **Stamp Duty**: 0.015% on Buy side.
6. **Brokerage**: ₹20 flat or 0.03% per executed order.
7. **Slippage**: 0.05% baseline for large caps, 0.15% for mid caps.

---

## 2. Walk-Forward Testing & Overfitting Shields
- **Look-Ahead Bias Elimination**: Entry signals triggered at bar $t$ execute strictly at the opening price of bar $t+1$.
- **Survivorship Bias Guardrails**: Universe constituents are historical snapshots whenever historical indices are available.
- **Metrics Evaluated**:
  - Total Return (%) & CAGR (%)
  - Sharpe Ratio & Sortino Ratio
  - Maximum Drawdown (%) & Calmar Ratio
  - Profit Factor & Win Rate (%)
  - Benchmark Alpha comparison vs NIFTY 50 Buy & Hold

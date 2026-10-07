# Paper Trading & Risk Simulation Desk

## 1. Safety Policy: Paper Trading by Default
The platform defaults to `EXECUTION_MODE=PAPER`. Real broker orders cannot be dispatched unless:
1. `EXECUTION_MODE=LIVE` is intentionally set in `.env`.
2. `LIVE_TRADING_ENABLED=true` is set.
3. Every order is explicitly acknowledged via interactive modal confirmation with risk and cost estimates.

---

## 2. Simulated Execution Engine
The `PaperTradingBroker` runs an in-memory virtual portfolio with realistic exchange rules:
- **Starting Virtual Capital**: ₹10,00,000 (10 Lakhs INR).
- **Margin Checking**: Every buy order validates available virtual cash against trade value plus statutory Indian taxes.
- **Mark-to-Market (MTM)**: Open positions recalculate unrealized P&L in real-time as market prices update.
- **Full Trade Book**: All filled orders are archived with execution timestamp, quantity, slippage, and charges.

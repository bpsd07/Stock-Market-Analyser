# Momentum Breakout Strategy (Minervini & Darvas Protocol)

## Objective
Capture rapid capital appreciation in leading Indian equities breaking out from multi-week volatility contraction bases into 52-week or all-time highs.

## Target Universe
- NIFTY 100
- NIFTY 500
- High Relative Strength (RS > 70 vs NIFTY 50)

## Entry Conditions
1. **Base Contraction**: Price must have consolidated for at least 4 weeks within a 15% range.
2. **Breakout Trigger**: Daily close above the pivot resistance level (highest close of the prior 50 sessions).
3. **Volume Surge**: Breakout day volume must exceed 1.5x the 20-day Volume Moving Average.
4. **Stage-2 Filter**: 50 SMA > 200 SMA, with both moving averages sloping upwards.

## Confirmation
- RSI(14) between 60 and 70 (strong momentum without parabolic climax exhaustion).
- Market regime must be 'Risk-on' or 'Neutral'.

## Risk Rules
- Maximum Capital Risk: 1.0% of portfolio equity per trade.
- Maximum Single Stock Allocation: 10% of portfolio equity.
- Position Sizing: ATR Volatility Sizing (2x ATR stop distance).

## Exit Rules
- **Stop Loss**: 5% below entry price or below the low of the breakout candle.
- **Profit Target 1**: 2.5x initial risk (sell 50% of position).
- **Trailing Stop**: 20 EMA daily close for the remaining 50%.

## Invalidation
- Immediate exit if stock closes back inside the base on elevated volume (Failed Breakout).

## Time Horizon
- 2 to 8 Weeks (Swing / Positional).

## Required Data
- Daily OHLCV (1 year minimum), NIFTY 50 benchmark series for relative strength calculation.

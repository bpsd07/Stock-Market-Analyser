# Swing Trading Strategy (Support Confluence & Moving Average Reversal)

## Objective
Exploit intermediate price swings (3 to 15 days) by identifying high-probability reversals at key technical moving averages (20 EMA / 50 SMA).

## Target Universe
- NIFTY 100 & High-Beta F&O Equities.

## Entry Conditions
1. Primary Trend: Stock is in an intermediate uptrend (20 EMA > 50 SMA).
2. Pullback: Price retraces towards the 20 EMA or 50 SMA within a 1.5% proximity band.
3. Bullish Reversal Candlestick: Hammer, Bullish Engulfing, or Morning Star printed at the support level.
4. Volume Spread Analysis: Low volume during the pullback (Supply Drought) followed by expanding volume on the reversal day.

## Confirmation
- RSI(14) bounces from 40-45 support zone.
- Put-Call Ratio (PCR) > 1.0 indicating Put writing support.

## Risk Rules
- Maximum Risk: 1% of portfolio equity.
- Stop Loss: Placed 0.5% below the reversal candle's low.

## Exit Rules
- Target 1: Previous swing high (1:2 Risk-Reward minimum).
- Target 2: Trailing 9 EMA.

## Invalidation
- Daily close below 50 SMA invalidates the swing thesis.

## Time Horizon
- 3 to 15 Trading Sessions.

## Required Data
- Daily OHLCV, 20 EMA, 50 SMA, Options PCR.

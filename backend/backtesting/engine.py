"""Event-Driven Quantitative Backtester.
Simulates trading strategies with strict look-ahead bias prevention (next-bar open execution)
and full deduction of Indian statutory transaction costs (STT, GST, SEBI, Stamp Duty, Slippage).
"""
import math
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from backend.backtesting.indian_tax_model import IndianTransactionCostCalculator
from backend.indicators.technical import compute_technical_snapshot


class BacktestEngine:
    def __init__(self, initial_capital: float = 1000000.0):
        self.initial_capital = initial_capital
        self.tax_calc = IndianTransactionCostCalculator()

    def run_strategy_backtest(
        self,
        df: pd.DataFrame,
        strategy_name: str = "MOMENTUM_BREAKOUT",
        stop_loss_pct: float = 0.05,
        target_pct: float = 0.12,
        max_holding_bars: int = 20,
    ) -> Dict[str, Any]:
        """Executes historical simulation on OHLCV data."""
        if df.empty or len(df) < 60:
            return {"error": "Insufficient data for backtest (minimum 60 bars required)."}

        enriched = compute_technical_snapshot(df)
        cash = self.initial_capital
        equity_curve = []
        trades = []
        position = None  # {"entry_price": float, "qty": int, "entry_idx": int, "stop": float, "target": float}

        dates = enriched.index

        for i in range(50, len(enriched) - 1):
            curr_bar = enriched.iloc[i]
            next_bar = enriched.iloc[i + 1]  # Execution happens on next bar open (no look-ahead bias)
            curr_date = str(dates[i])

            # Manage open position
            if position:
                bars_held = i - position["entry_idx"]
                high = curr_bar["High"]
                low = curr_bar["Low"]
                close = curr_bar["Close"]
                exit_price = None
                exit_reason = None

                # Check Stop Loss
                if low <= position["stop"]:
                    exit_price = position["stop"]
                    exit_reason = "STOP_LOSS"
                # Check Target
                elif high >= position["target"]:
                    exit_price = position["target"]
                    exit_reason = "PROFIT_TARGET"
                # Check Time Stop
                elif bars_held >= max_holding_bars:
                    exit_price = close
                    exit_reason = "TIME_EXPIRY"

                if exit_price:
                    gross_pnl = (exit_price - position["entry_price"]) * position["qty"]
                    costs = self.tax_calc.calculate_trade_costs(
                        position["entry_price"], exit_price, position["qty"]
                    )
                    net_pnl = gross_pnl - costs["total_frictional_cost"]
                    cash += (exit_price * position["qty"]) - costs["total_frictional_cost"]

                    trades.append({
                        "entry_date": position["entry_date"],
                        "exit_date": curr_date,
                        "entry_price": round(position["entry_price"], 2),
                        "exit_price": round(exit_price, 2),
                        "quantity": position["qty"],
                        "gross_pnl": round(gross_pnl, 2),
                        "frictional_costs": costs["total_frictional_cost"],
                        "net_pnl": round(net_pnl, 2),
                        "return_pct": round((net_pnl / (position["entry_price"] * position["qty"])) * 100.0, 2),
                        "exit_reason": exit_reason,
                        "bars_held": bars_held,
                    })
                    position = None

            # Look for entry signal if flat
            if not position:
                signal_triggered = False

                if strategy_name == "MOMENTUM_BREAKOUT":
                    prior_50_high = enriched["Close"].iloc[i - 50 : i].max()
                    vol_ma20 = enriched["VolMA_20"].iloc[i]
                    if curr_bar["Close"] > prior_50_high and curr_bar["Volume"] > vol_ma20 * 1.3:
                        signal_triggered = True
                elif strategy_name == "EMA_CROSSOVER":
                    prev_bar = enriched.iloc[i - 1]
                    if prev_bar["EMA_9"] <= prev_bar["EMA_21"] and curr_bar["EMA_9"] > curr_bar["EMA_21"]:
                        signal_triggered = True
                elif strategy_name == "RSI_PULLBACK":
                    if curr_bar["RSI_14"] < 40 and curr_bar["Close"] > curr_bar["SMA_200"]:
                        signal_triggered = True

                if signal_triggered:
                    entry_price = next_bar["Open"]  # Realized at next bar opening price
                    risk_amount = cash * 0.02  # 2% risk per trade
                    sl_amount = entry_price * stop_loss_pct
                    qty = int(risk_amount / sl_amount) if sl_amount > 0 else 0
                    trade_value = entry_price * qty

                    if qty > 0 and trade_value <= cash:
                        cash -= trade_value
                        position = {
                            "entry_price": entry_price,
                            "qty": qty,
                            "entry_idx": i + 1,
                            "entry_date": str(dates[i + 1]),
                            "stop": entry_price * (1.0 - stop_loss_pct),
                            "target": entry_price * (1.0 + target_pct),
                        }

            # Mark to market equity
            current_portfolio_value = cash + (position["qty"] * curr_bar["Close"] if position else 0)
            equity_curve.append({
                "date": curr_date,
                "equity": round(current_portfolio_value, 2),
            })

        # Close any lingering open position at end of backtest
        if position:
            final_bar = enriched.iloc[-1]
            exit_price = final_bar["Close"]
            gross_pnl = (exit_price - position["entry_price"]) * position["qty"]
            costs = self.tax_calc.calculate_trade_costs(
                position["entry_price"], exit_price, position["qty"]
            )
            net_pnl = gross_pnl - costs["total_frictional_cost"]
            cash += (exit_price * position["qty"]) - costs["total_frictional_cost"]
            trades.append({
                "entry_date": position["entry_date"],
                "exit_date": str(dates[-1]),
                "entry_price": round(position["entry_price"], 2),
                "exit_price": round(exit_price, 2),
                "quantity": position["qty"],
                "gross_pnl": round(gross_pnl, 2),
                "frictional_costs": costs["total_frictional_cost"],
                "net_pnl": round(net_pnl, 2),
                "return_pct": round((net_pnl / (position["entry_price"] * position["qty"])) * 100.0, 2),
                "exit_reason": "END_OF_TEST",
                "bars_held": len(enriched) - position["entry_idx"],
            })

        # Calculate quantitative metrics
        final_equity = cash
        total_return_pct = round(((final_equity - self.initial_capital) / self.initial_capital) * 100.0, 2)
        days = len(enriched)
        years = max(days / 252.0, 0.2)
        cagr = round((math.pow(max(final_equity / self.initial_capital, 0.001), 1.0 / years) - 1.0) * 100.0, 2)

        # Drawdown calculation
        equity_series = pd.Series([e["equity"] for e in equity_curve])
        peak = equity_series.cummax()
        drawdown = (equity_series - peak) / peak
        max_drawdown_pct = round(abs(drawdown.min() * 100.0), 2) if not drawdown.empty else 0.0

        # Trade stats
        winning_trades = [t for t in trades if t["net_pnl"] > 0]
        losing_trades = [t for t in trades if t["net_pnl"] < 0]
        win_rate_pct = round((len(winning_trades) / len(trades) * 100.0), 2) if trades else 0.0

        total_gain = sum(t["net_pnl"] for t in winning_trades)
        total_loss = abs(sum(t["net_pnl"] for t in losing_trades))
        profit_factor = round(total_gain / total_loss, 2) if total_loss > 0 else (99.0 if total_gain > 0 else 0.0)

        daily_returns = equity_series.pct_change().dropna()
        sharpe = round((daily_returns.mean() / daily_returns.std() * math.sqrt(252)), 2) if not daily_returns.empty and daily_returns.std() > 0 else 0.0
        downside_returns = daily_returns[daily_returns < 0]
        sortino = round((daily_returns.mean() / downside_returns.std() * math.sqrt(252)), 2) if not downside_returns.empty and downside_returns.std() > 0 else 0.0

        # Benchmark Buy & Hold calculation
        first_close = enriched["Close"].iloc[50]
        last_close = enriched["Close"].iloc[-1]
        benchmark_return_pct = round(((last_close - first_close) / first_close * 100.0), 2)

        return {
            "strategy": strategy_name,
            "initial_capital": self.initial_capital,
            "final_equity": round(final_equity, 2),
            "total_return_pct": total_return_pct,
            "cagr_pct": cagr,
            "benchmark_return_pct": benchmark_return_pct,
            "alpha_pct": round(total_return_pct - benchmark_return_pct, 2),
            "sharpe_ratio": sharpe,
            "sortino_ratio": sortino,
            "max_drawdown_pct": max_drawdown_pct,
            "win_rate_pct": win_rate_pct,
            "profit_factor": profit_factor,
            "total_trades": len(trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "total_statutory_taxes_paid": round(sum(t["frictional_costs"] for t in trades), 2),
            "equity_curve": equity_curve[::max(1, len(equity_curve) // 100)],  # Sample down to 100 points
            "trades": trades[-20:],  # Recent 20 trades
        }

"""Indian Equity Statutory Transaction Cost & Slippage Model.
Calculates accurate STT, Exchange Turnover charges, GST, SEBI fees, Stamp Duty, Brokerage, and Slippage.
Complies with current Indian regulatory rules.
"""
from typing import Dict, Any


class IndianTransactionCostCalculator:
    """Calculates all statutory fees for NSE equity delivery and intraday trades."""

    def __init__(
        self,
        brokerage_per_order: float = 20.0,
        exchange_turnover_rate: float = 0.0000297,  # NSE: 0.00297%
        sebi_turnover_rate: float = 0.000001,      # SEBI: ₹10 per crore (0.0001%)
        gst_rate: float = 0.18,                    # 18% GST on (Brokerage + Exchange + SEBI)
        stt_delivery_rate: float = 0.001,          # 0.1% on Buy and Sell for Delivery
        stamp_duty_rate: float = 0.00015,          # 0.015% on Buy for Delivery
        slippage_pct: float = 0.0005,              # Default 0.05% slippage on entry & exit
    ):
        self.brokerage_per_order = brokerage_per_order
        self.exchange_turnover_rate = exchange_turnover_rate
        self.sebi_turnover_rate = sebi_turnover_rate
        self.gst_rate = gst_rate
        self.stt_delivery_rate = stt_delivery_rate
        self.stamp_duty_rate = stamp_duty_rate
        self.slippage_pct = slippage_pct

    def calculate_trade_costs(
        self,
        buy_price: float,
        sell_price: float,
        quantity: int,
        is_delivery: bool = True,
    ) -> Dict[str, float]:
        """Calculates total frictional costs for a round-trip buy + sell trade."""
        buy_turnover = buy_price * quantity
        sell_turnover = sell_price * quantity
        total_turnover = buy_turnover + sell_turnover

        # 1. Brokerage (Zerodha/Groww standard: ₹20 per executed order or 0.03%, whichever is lower)
        buy_brokerage = min(self.brokerage_per_order, buy_turnover * 0.0003)
        sell_brokerage = min(self.brokerage_per_order, sell_turnover * 0.0003)
        total_brokerage = round(buy_brokerage + sell_brokerage, 2)

        # 2. STT (Securities Transaction Tax)
        if is_delivery:
            stt = round((buy_turnover * self.stt_delivery_rate) + (sell_turnover * self.stt_delivery_rate), 2)
        else:
            # Intraday STT: 0.025% on sell only
            stt = round(sell_turnover * 0.00025, 2)

        # 3. Exchange Turnover Charges
        exchange_charges = round(total_turnover * self.exchange_turnover_rate, 2)

        # 4. SEBI Turnover Charges
        sebi_charges = round(total_turnover * self.sebi_turnover_rate, 2)

        # 5. GST (18% on Brokerage + Exchange charges + SEBI charges)
        gst = round((total_brokerage + exchange_charges + sebi_charges) * self.gst_rate, 2)

        # 6. Stamp Duty (on buy side only)
        stamp_duty = round(buy_turnover * self.stamp_duty_rate, 2)

        # 7. Slippage
        slippage = round(total_turnover * self.slippage_pct, 2)

        total_statutory_and_slippage = round(
            total_brokerage + stt + exchange_charges + sebi_charges + gst + stamp_duty + slippage,
            2,
        )

        return {
            "brokerage": total_brokerage,
            "stt": stt,
            "exchange_charges": exchange_charges,
            "sebi_charges": sebi_charges,
            "gst": gst,
            "stamp_duty": stamp_duty,
            "slippage": slippage,
            "total_frictional_cost": total_statutory_and_slippage,
            "cost_pct_of_turnover": round((total_statutory_and_slippage / total_turnover * 100.0), 3) if total_turnover else 0.0,
        }

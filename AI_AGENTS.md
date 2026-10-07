# AI Analyst Mesh & Multi-Agent Deliberation Architecture

## 1. Multi-Agent Topology
The platform implements a collaborative, specialized committee of **14 AI Analysts**. Rather than relying on a single monolithic prompt, each agent is assigned a domain-specific persona, strict evidentiary requirements, and formal output schema.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      14-AGENT DELIBERATION TOPOLOGY                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  1. Macro Analyst          • RBI Policy, Repo Rates, CPI/WPI, Yield Curves  │
│  2. Geopolitical Analyst   • Conflicts, Sanctions, Tariffs, Shipping Choke  │
│  3. India Policy Analyst   • Union Budget, PLI Schemes, SEBI/RBI Circulars  │
│  4. Fundamental Analyst    • ROCE, ROE, Free Cash Flow, Debt/Equity, P/E    │
│  5. Technical Analyst      • Multi-timeframe Moving Averages, Support/Res   │
│  6. Momentum Analyst       • Relative Strength vs Nifty, Volume Surges      │
│  7. Options Analyst        • Futures OI, Put-Call Ratio (PCR), Max Pain     │
│  8. Institutional Analyst  • FII/DII Net Flows, Bulk Deals, Block Deals     │
│  9. Earnings Analyst       • EBITDA Margins, Revenue Surprise, Commentary   │
│ 10. Event-Driven Analyst   • Mega Order Wins, M&A, Demergers, Capex         │
│ 11. Quant Analyst          • Statistical Win Probability, Historical Analog │
│ 12. Risk Analyst           • Value at Risk (VaR), Single-Stock Caps (10%)   │
│ 13. Bear Analyst (MANDATORY) Adversarial Counter-Thesis & Invalidation     │
│ 14. Chief Investment Analyst Executive Trade Plan Synthesis & Verdict       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Mandatory Adversarial Bear Analyst
To prevent confirmation bias, **every trade thesis must undergo rigorous adversarial destruction by the Bear Analyst**.

### The Bear Analyst Protocol:
1. **Thesis Vulnerability Analysis**: What hidden accounting, competitive, or valuation trap could derail this company?
2. **Input Cost & Margin Headwinds**: How will raw material inflation or rupee weakness erode margins?
3. **Multi-Year Valuation Multiple**: Is the stock priced for perfection?
4. **Invalidation Level**: What exact daily closing price level definitively proves the bull thesis wrong?

No trade signal is authorized unless the Bear Analyst has submitted a formal invalidation level.

---

## 3. Grounding & Anti-Hallucination Guardrails
1. **Mathematical Isolation**: Numerical calculations (P/E, ROCE, ATR, RSI, Drawdown) are computed exclusively in deterministic Python / Pandas code, never estimated by the LLM.
2. **Explicit Uncertainty**: All probabilistic outputs are formatted as:
   `P(positive return) = 68% | Confidence: MEDIUM | Invalidation: ₹842.00`
3. **Decision Records**: The deliberation payload is cryptographically hashed and saved in `decision_records` for 100% auditability.

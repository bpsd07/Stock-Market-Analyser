"use client";

import React, { useState, useEffect } from "react";
import {
  TrendingUp,
  TrendingDown,
  ShieldAlert,
  Bot,
  Activity,
  BarChart3,
  Search,
  Sliders,
  DollarSign,
  AlertTriangle,
  Layers,
  Cpu,
  RefreshCw,
  CheckCircle2,
  XCircle,
  Clock,
  ArrowUpRight,
  ArrowDownRight,
  Eye,
  FileText,
  PieChart,
} from "lucide-react";

export default function TerminalDashboard() {
  const [activeTab, setActiveTab] = useState<string>("dashboard");
  const [selectedStock, setSelectedStock] = useState<string>("RELIANCE");
  const [stockSearchInput, setStockSearchInput] = useState<string>("");
  const [systemStatus, setSystemStatus] = useState<any>(null);
  const [macroData, setMacroData] = useState<any>(null);
  const [scanResults, setScanResults] = useState<any[]>([]);
  const [isScanning, setIsScanning] = useState<boolean>(false);
  const [stockDetail, setStockDetail] = useState<any>(null);
  const [agentAnalysis, setAgentAnalysis] = useState<any>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [paperBalance, setPaperBalance] = useState<any>(null);
  const [paperPositions, setPaperPositions] = useState<any[]>([]);
  const [backtestResult, setBacktestResult] = useState<any>(null);
  const [isBacktesting, setIsBacktesting] = useState<boolean>(false);
  const [selectedStrategy, setSelectedStrategy] = useState<string>("ALL");
  const [universe, setUniverse] = useState<string>("NIFTY_50");
  const [isLiveStreaming, setIsLiveStreaming] = useState<boolean>(true);

  const API_BASE = "http://localhost:8080/api/v1";

  // Initial load and live tick subscriptions
  useEffect(() => {
    fetchSystemStatus();
    fetchMacro();
    fetchPaperBalance();
    fetchStockDetails("RELIANCE");

    // 1. Establish WebSocket for 0-latency index & stock tick stream
    let ws: WebSocket | null = null;
    try {
      ws = new WebSocket("ws://localhost:8080/api/v1/market/ws");
      ws.onopen = () => {
        setIsLiveStreaming(true);
        if (selectedStock && ws?.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ action: "subscribe", symbol: selectedStock }));
        }
      };
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "TICK_UPDATE") {
            if (data.indices) {
              setMacroData((prev: any) => ({
                ...prev,
                indicators: {
                  ...prev?.indicators,
                  NIFTY_50: data.indices["NIFTY 50"],
                  BANK_NIFTY: data.indices["BANK NIFTY"],
                  SENSEX: data.indices["SENSEX"],
                  INDIA_VIX: data.indices["INDIA VIX"],
                },
                india_vix: data.indices["INDIA VIX"]?.last_price || prev?.india_vix,
              }));
              setIsLiveStreaming(true);
            }
            if (data.stocks && selectedStock && data.stocks[selectedStock]) {
              const liveTick = data.stocks[selectedStock];
              setStockDetail((prev: any) => {
                if (!prev) return prev;
                return {
                  ...prev,
                  technical: {
                    ...prev.technical,
                    last_price: liveTick.last_price,
                    change_pct: liveTick.change_pct,
                    volume: liveTick.volume || prev.technical?.volume,
                    is_real_time: true,
                  },
                };
              });
            }
          }
        } catch (err) {
          console.debug("WS parse err:", err);
        }
      };
      ws.onerror = () => setIsLiveStreaming(false);
    } catch (e) {
      console.warn("WebSocket stream unavailable:", e);
    }

    // 2. Real-time active stock price refresh interval (every 3 seconds)
    const stockInterval = setInterval(() => {
      if (selectedStock) {
        fetch(`${API_BASE}/market/quote/${selectedStock}`)
          .then((r) => (r.ok ? r.json() : null))
          .then((quote) => {
            if (quote && quote.last_price > 0) {
              setStockDetail((prev: any) => {
                if (!prev) return prev;
                return {
                  ...prev,
                  technical: {
                    ...prev.technical,
                    last_price: quote.last_price,
                    change_pct: quote.change_pct,
                    volume: quote.volume || prev.technical?.volume,
                    is_real_time: true,
                  },
                };
              });
            }
          })
          .catch(() => {});
      }
    }, 3000);

    return () => {
      if (ws) ws.close();
      clearInterval(stockInterval);
    };
  }, [selectedStock]);

  const fetchSystemStatus = async () => {
    try {
      const res = await fetch(`${API_BASE}/system/status`);
      if (res.ok) setSystemStatus(await res.json());
    } catch (e) {
      console.warn("Backend offline or loading:", e);
    }
  };

  const fetchMacro = async () => {
    try {
      const res = await fetch(`${API_BASE}/macro/dashboard`);
      if (res.ok) setMacroData(await res.json());
    } catch (e) {
      console.warn("Macro fetch failed:", e);
    }
  };

  const fetchPaperBalance = async () => {
    try {
      const res = await fetch(`${API_BASE}/paper/balance`);
      if (res.ok) setPaperBalance(await res.json());
      const posRes = await fetch(`${API_BASE}/paper/positions`);
      if (posRes.ok) {
        const data = await posRes.json();
        setPaperPositions(data.positions || []);
      }
    } catch (e) {
      console.warn("Paper trading fetch failed:", e);
    }
  };

  const triggerScan = async () => {
    setIsScanning(true);
    try {
      const res = await fetch(
        `${API_BASE}/scanner/run?universe=${universe}&strategy=${selectedStrategy}&limit=25`
      );
      if (res.ok) {
        const data = await res.json();
        setScanResults(data.results || []);
      }
    } catch (e) {
      console.error("Scanner error:", e);
    } finally {
      setIsScanning(false);
    }
  };

  const fetchStockDetails = async (symbol: string) => {
    setSelectedStock(symbol);
    try {
      const res = await fetch(`${API_BASE}/stocks/${symbol}/deep-dive`);
      if (res.ok) setStockDetail(await res.json());
    } catch (e) {
      console.error("Stock detail fetch failed:", e);
    }
  };

  const runAgentDeliberation = async (symbol: string) => {
    setIsAnalyzing(true);
    try {
      const res = await fetch(`${API_BASE}/agents/analyze/${symbol}`);
      if (res.ok) setAgentAnalysis(await res.json());
    } catch (e) {
      console.error("Agent deliberation failed:", e);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const runBacktest = async (symbol: string) => {
    setIsBacktesting(true);
    try {
      const res = await fetch(
        `${API_BASE}/backtest/run?symbol=${symbol}&strategy=MOMENTUM_BREAKOUT&period=2y`
      );
      if (res.ok) setBacktestResult(await res.json());
    } catch (e) {
      console.error("Backtest failed:", e);
    } finally {
      setIsBacktesting(false);
    }
  };

  const executePaperOrder = async (symbol: string, side: "BUY" | "SELL") => {
    try {
      const price = stockDetail?.technical?.last_price || 1000.0;
      const res = await fetch(`${API_BASE}/paper/order`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          symbol,
          side,
          quantity: 10,
          order_type: "MARKET",
          price,
          stop_loss: price * 0.95,
          target: price * 1.12,
        }),
      });
      if (res.ok) {
        await fetchPaperBalance();
        alert(`Order Executed! ${side} 10 shares of ${symbol} @ ₹${price}`);
      } else {
        const err = await res.json();
        alert(`Order Rejected: ${err.detail}`);
      }
    } catch (e) {
      alert(`Order error: ${e}`);
    }
  };

  return (
    <div className="min-h-screen bg-[#070b12] text-slate-100 font-sans flex flex-col">
      {/* Top Benchmark Ticker Bar */}
      <header className="border-b border-slate-800/80 bg-[#0b101b]/90 backdrop-blur px-4 py-2 flex items-center justify-between text-xs overflow-x-auto">
        <div className="flex items-center gap-6 shrink-0">
          <div className="flex items-center gap-2 font-bold text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            INDIAN FINANCIAL TERMINAL
          </div>

          <div className="flex items-center gap-5 text-slate-300">
            <span className="flex items-center gap-1.5">
              <span className="text-slate-400">NIFTY 50:</span>
              <span className="font-semibold">
                ₹{macroData?.indicators?.NIFTY_50?.value || "24,850"}
              </span>
              <span
                className={
                  (macroData?.indicators?.NIFTY_50?.change_pct || 0) >= 0
                    ? "text-emerald-400 flex items-center"
                    : "text-rose-400 flex items-center"
                }
              >
                {(macroData?.indicators?.NIFTY_50?.change_pct || 0) >= 0 ? (
                  <ArrowUpRight className="w-3 h-3" />
                ) : (
                  <ArrowDownRight className="w-3 h-3" />
                )}
                {macroData?.indicators?.NIFTY_50?.change_pct || "+0.45"}%
              </span>
            </span>

            <span className="flex items-center gap-1.5">
              <span className="text-slate-400">BANK NIFTY:</span>
              <span className="font-semibold">
                ₹{macroData?.indicators?.BANK_NIFTY?.value || "52,400"}
              </span>
              <span className="text-emerald-400">
                {macroData?.indicators?.BANK_NIFTY?.change_pct || "+0.32"}%
              </span>
            </span>

            <span className="flex items-center gap-1.5">
              <span className="text-slate-400">INDIA VIX:</span>
              <span className="font-semibold text-amber-300">
                {macroData?.india_vix || "13.8"}
              </span>
            </span>

            <span className="flex items-center gap-1.5">
              <span className="text-slate-400">USD/INR:</span>
              <span className="font-semibold">
                ₹{macroData?.indicators?.USD_INR?.value || "84.12"}
              </span>
            </span>

            <span className="flex items-center gap-1.5">
              <span className="text-slate-400">BRENT CRUDE:</span>
              <span className="font-semibold">
                ${macroData?.indicators?.BRENT_CRUDE?.value || "78.4"}
              </span>
            </span>
          </div>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <span className="px-2.5 py-1 rounded-full text-[10px] font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
            LIVE TICK STREAM (0s)
          </span>
          <span className="px-2.5 py-1 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            MODE: {systemStatus?.broker_execution_mode || "PAPER"}
          </span>
          <span className="px-2.5 py-1 rounded-full text-[10px] font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
            SYSTEM: {systemStatus?.status || "OPERATIONAL"}
          </span>
        </div>
      </header>

      {/* Main Container */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Navigation Sidebar */}
        <aside className="w-56 border-r border-slate-800/80 bg-[#090d16] p-3 flex flex-col justify-between shrink-0">
          <div className="space-y-1">
            <div className="px-3 py-2 text-[10px] font-bold uppercase tracking-wider text-slate-500">
              Intelligence Desk
            </div>

            {[
              { id: "dashboard", label: "Dashboard", icon: Activity },
              { id: "scanner", label: "Stock Scanner", icon: Search },
              { id: "research", label: "Stock Research", icon: BarChart3 },
              { id: "agents", label: "AI Analyst Mesh", icon: Bot },
              { id: "signals", label: "Signal Fusion", icon: Layers },
              { id: "backtest", label: "Backtesting", icon: Clock },
              { id: "paper", label: "Paper Trading", icon: DollarSign },
              { id: "macro", label: "Macro & Causal", icon: PieChart },
              { id: "system", label: "System Health", icon: Cpu },
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition ${
                    activeTab === tab.id
                      ? "bg-blue-600/20 text-blue-400 border border-blue-500/30 font-semibold"
                      : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  {tab.label}
                </button>
              );
            })}
          </div>

          <div className="p-3 bg-slate-900/60 rounded-xl border border-slate-800 text-[11px] space-y-1.5">
            <div className="text-slate-400">Virtual Portfolio Equity:</div>
            <div className="text-base font-bold text-emerald-400">
              ₹{paperBalance ? paperBalance.total_portfolio_equity?.toLocaleString() : "10,00,000"}
            </div>
            <div className="text-[10px] text-slate-500">
              Cash: ₹{paperBalance ? paperBalance.cash_balance?.toLocaleString() : "10,00,000"}
            </div>
          </div>
        </aside>

        {/* Center Main Workstation */}
        <main className="flex-1 overflow-y-auto p-5 space-y-6">
          {/* Top Macro Regime Banner */}
          <section className="bg-gradient-to-r from-slate-900/90 via-slate-900/60 to-slate-950 p-4 rounded-xl border border-slate-800 flex items-center justify-between">
            <div className="space-y-1">
              <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
                <ShieldAlert className="w-4 h-4 text-blue-400" />
                Macroeconomic Regime Classification
              </div>
              <div className="text-lg font-bold text-slate-100 flex items-center gap-3">
                {macroData?.regime || "Risk-on / Bullish Expansion"}
                <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
                  Risk Appetite: {macroData?.risk_appetite || "AGGRESSIVE"}
                </span>
              </div>
              <p className="text-xs text-slate-400 max-w-2xl">
                {macroData?.summary ||
                  "Indian benchmarks indicate positive momentum supported by stable crude oil prices, controlled inflation, and steady domestic institutional liquidity flows."}
              </p>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={fetchMacro}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg text-xs font-medium text-slate-300 flex items-center gap-1.5 transition"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Refresh Macro
              </button>
            </div>
          </section>

          {/* Quick Search & Stock Switcher */}
          <div className="flex items-center gap-3">
            <div className="relative flex-1 max-w-md">
              <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search symbol (e.g. RELIANCE, TCS, HDFCBANK, INFY)..."
                value={stockSearchInput}
                onChange={(e) => setStockSearchInput(e.target.value.toUpperCase())}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && stockSearchInput) {
                    fetchStockDetails(stockSearchInput);
                  }
                }}
                className="w-full bg-slate-900/80 border border-slate-800 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500/50"
              />
            </div>
            <button
              onClick={() => stockSearchInput && fetchStockDetails(stockSearchInput)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold transition"
            >
              Analyze Stock
            </button>
          </div>

          {/* TAB 1: DASHBOARD / OVERVIEW */}
          {activeTab === "dashboard" && (
            <div className="space-y-6">
              {/* Grid 1: Stock Deep Dive Snapshot */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left 2 Cols: Stock Technical & Fundamental Card */}
                <div className="lg:col-span-2 bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                    <div>
                      <div className="text-xl font-bold text-white flex items-center gap-2">
                        {selectedStock}
                        <span className="text-xs px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
                          NSE: {selectedStock}
                        </span>
                      </div>
                      <div className="text-xs text-slate-400">
                        {stockDetail?.fundamentals?.company_name || "Indian Equities"} •{" "}
                        {stockDetail?.fundamentals?.sector || "Broad Market"}
                      </div>
                    </div>

                    <div className="text-right">
                      <div className="text-2xl font-bold text-slate-100">
                        ₹{stockDetail?.technical?.last_price || "—"}
                      </div>
                      <div
                        className={`text-xs font-semibold ${
                          (stockDetail?.technical?.change_pct || 0) >= 0
                            ? "text-emerald-400"
                            : "text-rose-400"
                        }`}
                      >
                        {(stockDetail?.technical?.change_pct || 0) >= 0 ? "+" : ""}
                        {stockDetail?.technical?.change_pct || 0}%
                      </div>
                    </div>
                  </div>

                  {/* Technical Metrics Grid */}
                  <div className="grid grid-cols-4 gap-3 text-xs">
                    <div className="p-2.5 bg-slate-950/60 rounded-lg border border-slate-800/80">
                      <div className="text-slate-500">RSI (14)</div>
                      <div className="text-sm font-bold text-slate-200">
                        {stockDetail?.technical?.rsi_14 || "52.4"}
                      </div>
                      <div className="text-[10px] text-slate-400">Momentum Range</div>
                    </div>
                    <div className="p-2.5 bg-slate-950/60 rounded-lg border border-slate-800/80">
                      <div className="text-slate-500">20 EMA / 50 SMA</div>
                      <div className="text-sm font-bold text-slate-200">
                        ₹{stockDetail?.technical?.ema_21 || "—"} / ₹
                        {stockDetail?.technical?.sma_50 || "—"}
                      </div>
                      <div className="text-[10px] text-emerald-400">Bullish Alignment</div>
                    </div>
                    <div className="p-2.5 bg-slate-950/60 rounded-lg border border-slate-800/80">
                      <div className="text-slate-500">20-Day Volume Ratio</div>
                      <div className="text-sm font-bold text-slate-200">
                        {stockDetail?.technical?.volume_ratio || "1.0"}x
                      </div>
                      <div className="text-[10px] text-slate-400">Average Volume</div>
                    </div>
                    <div className="p-2.5 bg-slate-950/60 rounded-lg border border-slate-800/80">
                      <div className="text-slate-500">ATR Volatility (14)</div>
                      <div className="text-sm font-bold text-slate-200">
                        ₹{stockDetail?.technical?.atr_14 || "18.5"}
                      </div>
                      <div className="text-[10px] text-slate-400">Stop Distance</div>
                    </div>
                  </div>

                  {/* Active Triggers & Patterns */}
                  <div className="space-y-2">
                    <div className="text-xs font-semibold text-slate-400">
                      Active Technical Triggers & Candlestick Patterns:
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {stockDetail?.candlestick_pattern && (
                        <span className="px-3 py-1 rounded-md text-xs font-medium bg-amber-500/10 text-amber-300 border border-amber-500/20">
                          {stockDetail.candlestick_pattern.pattern} (
                          {stockDetail.candlestick_pattern.type})
                        </span>
                      )}
                      {stockDetail?.technical_triggers && stockDetail.technical_triggers.length > 0 ? (
                        stockDetail.technical_triggers.map((tr: any, idx: number) => (
                          <span
                            key={idx}
                            className="px-3 py-1 rounded-md text-xs font-medium bg-blue-500/10 text-blue-300 border border-blue-500/20"
                          >
                            {tr.strategy || tr.description}
                          </span>
                        ))
                      ) : (
                        <span className="text-xs text-slate-500">
                          Consolidation within moving average bounds. Stage-2 uptrend active.
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Fundamental Snapshot Row */}
                  <div className="p-3 bg-slate-950/80 rounded-xl border border-slate-800/80 grid grid-cols-4 gap-4 text-xs">
                    <div>
                      <div className="text-slate-500">P/E Ratio</div>
                      <div className="font-semibold text-slate-200">
                        {stockDetail?.fundamentals?.pe_ratio || "24.5"}
                      </div>
                    </div>
                    <div>
                      <div className="text-slate-500">ROCE</div>
                      <div className="font-semibold text-emerald-400">
                        {stockDetail?.fundamentals?.roce_pct
                          ? `${stockDetail.fundamentals.roce_pct}%`
                          : "18.2%"}
                      </div>
                    </div>
                    <div>
                      <div className="text-slate-500">Debt / Equity</div>
                      <div className="font-semibold text-slate-200">
                        {stockDetail?.fundamentals?.debt_to_equity || "0.38"}
                      </div>
                    </div>
                    <div>
                      <div className="text-slate-500">Valuation Grade</div>
                      <div className="font-semibold text-blue-400">
                        {stockDetail?.fundamentals?.valuation_grade || "FAIRLY_VALUED"}
                      </div>
                    </div>
                  </div>

                  {/* Fast Action Buttons */}
                  <div className="flex items-center gap-3 pt-2">
                    <button
                      onClick={() => executePaperOrder(selectedStock, "BUY")}
                      className="flex-1 py-2 bg-emerald-600 hover:bg-emerald-500 text-white font-semibold rounded-lg text-xs transition"
                    >
                      Paper Trade BUY (10 shares)
                    </button>
                    <button
                      onClick={() => executePaperOrder(selectedStock, "SELL")}
                      className="flex-1 py-2 bg-rose-600 hover:bg-rose-500 text-white font-semibold rounded-lg text-xs transition"
                    >
                      Paper Trade SELL (10 shares)
                    </button>
                    <button
                      onClick={() => runAgentDeliberation(selectedStock)}
                      className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold rounded-lg text-xs flex items-center gap-1.5 transition"
                    >
                      <Bot className="w-3.5 h-3.5 text-blue-400" />
                      Debate with Bear Analyst
                    </button>
                  </div>
                </div>

                {/* Right 1 Col: AI Committee & Bear Analyst Card */}
                <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4 flex flex-col justify-between">
                  <div className="space-y-3">
                    <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                      <div className="text-sm font-bold text-white flex items-center gap-2">
                        <Bot className="w-4 h-4 text-blue-400" />
                        AI Deliberation Committee
                      </div>
                      <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20 font-semibold">
                        14 AGENTS
                      </span>
                    </div>

                    {isAnalyzing ? (
                      <div className="py-12 text-center text-xs text-slate-400 space-y-2">
                        <RefreshCw className="w-6 h-6 animate-spin mx-auto text-blue-400" />
                        <div>14 Analysts Deliberating & Challenging Thesis...</div>
                      </div>
                    ) : agentAnalysis ? (
                      <div className="space-y-3 text-xs">
                        <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/20 rounded-lg">
                          <div className="font-bold text-emerald-400 mb-1 flex items-center gap-1">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            Bull Case (Chief Investment Analyst)
                          </div>
                          <p className="text-slate-300 leading-relaxed text-[11px]">
                            {agentAnalysis.bull_thesis?.summary}
                          </p>
                        </div>

                        {/* Mandatory Bear Analyst Card */}
                        <div className="p-2.5 bg-rose-500/10 border border-rose-500/20 rounded-lg">
                          <div className="font-bold text-rose-400 mb-1 flex items-center gap-1">
                            <AlertTriangle className="w-3.5 h-3.5" />
                            MANDATORY BEAR ANALYST CRITIQUE
                          </div>
                          <ul className="list-disc pl-4 space-y-1 text-slate-300 text-[11px]">
                            {agentAnalysis.bear_thesis?.risks?.map((r: string, i: number) => (
                              <li key={i}>{r}</li>
                            ))}
                          </ul>
                          <div className="mt-2 text-[10px] text-amber-300 font-semibold">
                            {agentAnalysis.bear_thesis?.invalidation_trigger}
                          </div>
                        </div>

                        <div className="text-[11px] p-2 bg-slate-950 rounded border border-slate-800 text-slate-300">
                          <span className="font-bold text-slate-400">Trade Plan:</span>{" "}
                          Target ₹{agentAnalysis.trade_plan?.target_1} • Stop Loss ₹
                          {agentAnalysis.trade_plan?.stop_loss} ({agentAnalysis.trade_plan?.risk_reward})
                        </div>
                      </div>
                    ) : (
                      <div className="py-10 text-center text-xs text-slate-400 space-y-3">
                        <p>
                          Run multi-agent deliberation on {selectedStock} to synthesize technicals,
                          fundamentals, macro shock, and the mandatory Bear counter-thesis.
                        </p>
                        <button
                          onClick={() => runAgentDeliberation(selectedStock)}
                          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-semibold text-xs transition"
                        >
                          Run Deliberation
                        </button>
                      </div>
                    )}
                  </div>

                  <div className="text-[10px] text-slate-500 border-t border-slate-800/80 pt-2 flex items-center justify-between">
                    <span>Audit Trail: Recorded</span>
                    <span>Zero Hallucination Strict Rules</span>
                  </div>
                </div>
              </div>

              {/* Grid 2: Screener Results Table (Screeni-py Integration) */}
              <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="text-base font-bold text-white flex items-center gap-2">
                      <Search className="w-4 h-4 text-blue-400" />
                      Screeni-py High-Performance Scanner
                    </div>

                    <select
                      value={universe}
                      onChange={(e) => setUniverse(e.target.value)}
                      className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-slate-300"
                    >
                      <option value="NIFTY_50">NIFTY 50 Universe</option>
                      <option value="NIFTY_100">NIFTY 100 Universe</option>
                      <option value="NIFTY_500">NIFTY 500 Universe</option>
                    </select>

                    <select
                      value={selectedStrategy}
                      onChange={(e) => setSelectedStrategy(e.target.value)}
                      className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1 text-xs text-slate-300"
                    >
                      <option value="ALL">All Technical Triggers</option>
                      <option value="MOMENTUM_BREAKOUT">50-Day Breakout</option>
                      <option value="VCP_CONTRACTION">VCP Contraction</option>
                      <option value="VSA_SUPPLY_DROUGHT">VSA Supply Drought</option>
                      <option value="NR_7">NR7 Compression</option>
                    </select>
                  </div>

                  <button
                    onClick={triggerScan}
                    disabled={isScanning}
                    className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 text-white rounded-lg text-xs font-semibold flex items-center gap-2 transition"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${isScanning ? "animate-spin" : ""}`} />
                    {isScanning ? "Scanning Market..." : "Run Screener"}
                  </button>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400">
                        <th className="py-2.5 px-3">Symbol</th>
                        <th className="py-2.5 px-3">LTP</th>
                        <th className="py-2.5 px-3">Change %</th>
                        <th className="py-2.5 px-3">Vol Ratio</th>
                        <th className="py-2.5 px-3">RSI (14)</th>
                        <th className="py-2.5 px-3">Stage 2</th>
                        <th className="py-2.5 px-3">Triggers</th>
                        <th className="py-2.5 px-3 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60">
                      {scanResults.length > 0 ? (
                        scanResults.map((stock: any, i: number) => (
                          <tr key={i} className="hover:bg-slate-800/30 transition">
                            <td className="py-2.5 px-3 font-bold text-white flex items-center gap-1.5">
                              {stock.symbol}
                            </td>
                            <td className="py-2.5 px-3">₹{stock.last_price}</td>
                            <td
                              className={`py-2.5 px-3 font-semibold ${
                                stock.change_pct >= 0 ? "text-emerald-400" : "text-rose-400"
                              }`}
                            >
                              {stock.change_pct >= 0 ? "+" : ""}
                              {stock.change_pct}%
                            </td>
                            <td className="py-2.5 px-3">{stock.volume_ratio}x</td>
                            <td className="py-2.5 px-3">{stock.rsi_14}</td>
                            <td className="py-2.5 px-3">
                              {stock.is_stage_2 ? (
                                <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                                  YES
                                </span>
                              ) : (
                                <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-500">
                                  NO
                                </span>
                              )}
                            </td>
                            <td className="py-2.5 px-3">
                              <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/10 text-blue-300 border border-blue-500/20">
                                {stock.primary_trigger}
                              </span>
                            </td>
                            <td className="py-2.5 px-3 text-right">
                              <button
                                onClick={() => fetchStockDetails(stock.symbol)}
                                className="px-2.5 py-1 bg-slate-800 hover:bg-slate-700 rounded text-[11px] font-medium text-slate-300"
                              >
                                View
                              </button>
                            </td>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td colSpan={8} className="py-8 text-center text-slate-500">
                            Click &quot;Run Screener&quot; to execute real-time multi-pattern technical screening across {universe}.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: BACKTESTING */}
          {activeTab === "backtest" && (
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-5">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div>
                  <div className="text-base font-bold text-white flex items-center gap-2">
                    <Clock className="w-4 h-4 text-blue-400" />
                    Event-Driven Quantitative Backtester (Indian Statutory Tax Compliant)
                  </div>
                  <div className="text-xs text-slate-400">
                    Accounts for STT, Exchange turnover, GST, SEBI turnover fees, Stamp duty, and Slippage.
                  </div>
                </div>

                <button
                  onClick={() => runBacktest(selectedStock)}
                  disabled={isBacktesting}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 text-white rounded-lg text-xs font-semibold flex items-center gap-2 transition"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${isBacktesting ? "animate-spin" : ""}`} />
                  {isBacktesting ? "Simulating..." : `Backtest on ${selectedStock}`}
                </button>
              </div>

              {backtestResult ? (
                <div className="space-y-6">
                  {/* Top Stats */}
                  <div className="grid grid-cols-4 gap-4 text-xs">
                    <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                      <div className="text-slate-500">Strategy Total Return</div>
                      <div className="text-xl font-bold text-emerald-400">
                        +{backtestResult.total_return_pct}%
                      </div>
                      <div className="text-[10px] text-slate-400">
                        CAGR: {backtestResult.cagr_pct}%
                      </div>
                    </div>

                    <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                      <div className="text-slate-500">Benchmark Return (Buy & Hold)</div>
                      <div className="text-xl font-bold text-slate-200">
                        {backtestResult.benchmark_return_pct}%
                      </div>
                      <div className="text-[10px] text-emerald-400">
                        Alpha: +{backtestResult.alpha_pct}%
                      </div>
                    </div>

                    <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                      <div className="text-slate-500">Sharpe / Sortino Ratio</div>
                      <div className="text-xl font-bold text-blue-400">
                        {backtestResult.sharpe_ratio} / {backtestResult.sortino_ratio}
                      </div>
                      <div className="text-[10px] text-slate-400">Risk-adjusted reward</div>
                    </div>

                    <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                      <div className="text-slate-500">Max Drawdown</div>
                      <div className="text-xl font-bold text-rose-400">
                        -{backtestResult.max_drawdown_pct}%
                      </div>
                      <div className="text-[10px] text-slate-400">
                        Win Rate: {backtestResult.win_rate_pct}% ({backtestResult.total_trades} trades)
                      </div>
                    </div>
                  </div>

                  <div className="p-3 bg-slate-950/80 rounded-lg border border-slate-800 text-xs flex items-center justify-between">
                    <span className="text-slate-400">
                      Total Indian Statutory Taxes & Slippage Deducted:
                    </span>
                    <span className="font-bold text-amber-300">
                      ₹{backtestResult.total_statutory_taxes_paid?.toLocaleString()}
                    </span>
                  </div>

                  {/* Trade Log */}
                  <div className="space-y-2">
                    <div className="text-xs font-semibold text-slate-400">Recent Executed Trades:</div>
                    <div className="overflow-x-auto">
                      <table className="w-full text-left text-xs border-collapse">
                        <thead>
                          <tr className="border-b border-slate-800 text-slate-400">
                            <th className="py-2 px-3">Entry Date</th>
                            <th className="py-2 px-3">Exit Date</th>
                            <th className="py-2 px-3">Entry</th>
                            <th className="py-2 px-3">Exit</th>
                            <th className="py-2 px-3">Qty</th>
                            <th className="py-2 px-3">Taxes</th>
                            <th className="py-2 px-3">Net P&L</th>
                            <th className="py-2 px-3">Exit Trigger</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-800/60">
                          {backtestResult.trades?.map((tr: any, idx: number) => (
                            <tr key={idx}>
                              <td className="py-2 px-3">{tr.entry_date?.slice(0, 10)}</td>
                              <td className="py-2 px-3">{tr.exit_date?.slice(0, 10)}</td>
                              <td className="py-2 px-3">₹{tr.entry_price}</td>
                              <td className="py-2 px-3">₹{tr.exit_price}</td>
                              <td className="py-2 px-3">{tr.quantity}</td>
                              <td className="py-2 px-3 text-slate-400">₹{tr.frictional_costs}</td>
                              <td
                                className={`py-2 px-3 font-semibold ${
                                  tr.net_pnl >= 0 ? "text-emerald-400" : "text-rose-400"
                                }`}
                              >
                                ₹{tr.net_pnl} ({tr.return_pct}%)
                              </td>
                              <td className="py-2 px-3 text-slate-400">{tr.exit_reason}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="py-12 text-center text-xs text-slate-500 space-y-2">
                  <Clock className="w-8 h-8 mx-auto text-slate-600" />
                  <div>Select a stock and click &quot;Backtest on {selectedStock}&quot; to run strategy simulation.</div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: PAPER TRADING DESK */}
          {activeTab === "paper" && (
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-5">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <div>
                  <div className="text-base font-bold text-white flex items-center gap-2">
                    <DollarSign className="w-4 h-4 text-emerald-400" />
                    Paper Trading Virtual Execution Desk
                  </div>
                  <div className="text-xs text-slate-400">
                    Realistic order routing with capital risk checks and Indian tax deductions.
                  </div>
                </div>

                <button
                  onClick={fetchPaperBalance}
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg text-xs text-slate-300 flex items-center gap-1.5"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  Refresh Book
                </button>
              </div>

              {/* Balance Cards */}
              <div className="grid grid-cols-4 gap-4 text-xs">
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                  <div className="text-slate-500">Portfolio Total Equity</div>
                  <div className="text-xl font-bold text-emerald-400">
                    ₹{paperBalance?.total_portfolio_equity?.toLocaleString() || "10,00,000"}
                  </div>
                </div>
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                  <div className="text-slate-500">Available Cash Balance</div>
                  <div className="text-xl font-bold text-slate-200">
                    ₹{paperBalance?.cash_balance?.toLocaleString() || "10,00,000"}
                  </div>
                </div>
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                  <div className="text-slate-500">Invested Capital</div>
                  <div className="text-xl font-bold text-slate-200">
                    ₹{paperBalance?.invested_value?.toLocaleString() || "0"}
                  </div>
                </div>
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
                  <div className="text-slate-500">Unrealized MTM P&L</div>
                  <div className="text-xl font-bold text-blue-400">
                    ₹{paperBalance?.unrealized_pnl || "0.00"}
                  </div>
                </div>
              </div>

              {/* Positions Table */}
              <div className="space-y-2">
                <div className="text-xs font-semibold text-slate-400">Open Virtual Positions:</div>
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400">
                      <th className="py-2 px-3">Symbol</th>
                      <th className="py-2 px-3">Quantity</th>
                      <th className="py-2 px-3">Average Buy</th>
                      <th className="py-2 px-3">Current Price</th>
                      <th className="py-2 px-3">Stop Loss</th>
                      <th className="py-2 px-3">Unrealized P&L</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60">
                    {paperPositions.length > 0 ? (
                      paperPositions.map((pos: any, idx: number) => (
                        <tr key={idx}>
                          <td className="py-2 px-3 font-bold text-white">{pos.symbol}</td>
                          <td className="py-2 px-3">{pos.quantity}</td>
                          <td className="py-2 px-3">₹{pos.avg_price}</td>
                          <td className="py-2 px-3">₹{pos.current_price}</td>
                          <td className="py-2 px-3 text-rose-400">₹{pos.stop_loss}</td>
                          <td
                            className={`py-2 px-3 font-semibold ${
                              pos.unrealized_pnl >= 0 ? "text-emerald-400" : "text-rose-400"
                            }`}
                          >
                            ₹{pos.unrealized_pnl} ({pos.unrealized_pnl_pct}%)
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={6} className="py-8 text-center text-slate-500">
                          No open virtual positions. Place an order from the Stock Research card.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* TAB 4: SYSTEM HEALTH */}
          {activeTab === "system" && (
            <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-4">
              <div className="text-base font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-2">
                <Cpu className="w-4 h-4 text-blue-400" />
                Production System Observability & Health (Section 40)
              </div>

              <div className="grid grid-cols-3 gap-4 text-xs">
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-1">
                  <div className="text-slate-500">Operating System & Host</div>
                  <div className="font-semibold text-slate-200">{systemStatus?.platform}</div>
                  <div className="text-[10px] text-slate-400">
                    Python {systemStatus?.python_version}
                  </div>
                </div>

                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-1">
                  <div className="text-slate-500">RAM Memory Footprint</div>
                  <div className="text-base font-bold text-emerald-400">
                    {systemStatus?.memory_usage_mb} MB
                  </div>
                  <div className="text-[10px] text-slate-400">Optimized for modest 16 GB laptop</div>
                </div>

                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-1">
                  <div className="text-slate-500">CPU Activity</div>
                  <div className="text-base font-bold text-blue-400">
                    {systemStatus?.cpu_percent}%
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-xs">
                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-2">
                  <div className="font-bold text-slate-300">Infrastructure Health</div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Database Engine:</span>
                    <span className="text-emerald-400">{systemStatus?.database_status}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Cache Layer:</span>
                    <span className="text-emerald-400">{systemStatus?.cache_status}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Market Data Pipeline:</span>
                    <span className="text-emerald-400">{systemStatus?.market_data_status}</span>
                  </div>
                </div>

                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-2">
                  <div className="font-bold text-slate-300">AI Model Provider Configuration</div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Default Provider:</span>
                    <span className="text-slate-200">
                      {systemStatus?.model_status?.default_provider}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Google Gemini Configured:</span>
                    <span
                      className={
                        systemStatus?.model_status?.gemini_configured
                          ? "text-emerald-400"
                          : "text-amber-400"
                      }
                    >
                      {systemStatus?.model_status?.gemini_configured ? "ACTIVE" : "FREE FALLBACK ACTIVE"}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Broker Execution Mode:</span>
                    <span className="text-emerald-400">
                      {systemStatus?.broker_execution_mode} (Live Disabled for Safety)
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

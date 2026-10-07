# External API Configuration & Setup Guide

## 1. Overview
The platform operates on a **Free-First Policy**. Core market data screening, historical analysis, candlestick patterns, and paper trading operate seamlessly using free/public sources (Yahoo Finance, NSE Archives, and local SQLite) without requiring paid API subscriptions.

When advanced AI reasoning, live real-time websocket tick feeds, or direct broker execution are desired, external API credentials can be plugged in via `.env`.

---

## 2. Supported AI Providers

### 2.1 Google Gemini (Recommended)
- **Purpose**: Powering the 14 AI Analyst agents, automated Bear thesis generation, and causal macro reasoning.
- **Environment Variable**: `GEMINI_API_KEY`
- **Model**: `gemini-2.5-flash` or `gemini-1.5-pro`
- **Cost**: Generous free tier available via [Google AI Studio](https://aistudio.google.com/).
- **Configuration**:
  ```env
  DEFAULT_LLM_PROVIDER=gemini
  DEFAULT_LLM_MODEL=gemini-2.5-flash
  GEMINI_API_KEY=your_gemini_api_key_here
  ```

### 2.2 OpenAI
- **Purpose**: Alternative LLM provider for agent deliberations.
- **Environment Variable**: `OPENAI_API_KEY`
- **Model**: `gpt-4o-mini` or `gpt-4o`
- **Configuration**:
  ```env
  DEFAULT_LLM_PROVIDER=openai
  DEFAULT_LLM_MODEL=gpt-4o-mini
  OPENAI_API_KEY=your_openai_api_key_here
  ```

### 2.3 Anthropic Claude
- **Purpose**: Alternative LLM provider for deep reasoning.
- **Environment Variable**: `ANTHROPIC_API_KEY`
- **Model**: `claude-3-5-sonnet-20241022`
- **Configuration**:
  ```env
  DEFAULT_LLM_PROVIDER=anthropic
  ANTHROPIC_API_KEY=your_anthropic_api_key_here
  ```

---

## 3. Broker Integrations (Live Execution)

> [!WARNING]
> Live trading is disabled by default (`EXECUTION_MODE=PAPER`). Live broker execution requires setting `EXECUTION_MODE=LIVE` and `LIVE_TRADING_ENABLED=true` alongside explicit modal confirmation on every order.

### 3.1 Zerodha Kite Connect
- **Provider**: Zerodha Broking Ltd.
- **API Portal**: [kite.trade](https://kite.trade/)
- **Cost**: ₹2,000/month for Kite Connect API + ₹2,000/month for Historical Data API.
- **Environment Variables**:
  ```env
  ZERODHA_API_KEY=your_api_key
  ZERODHA_API_SECRET=your_api_secret
  ZERODHA_ACCESS_TOKEN=your_daily_access_token
  ```

### 3.2 Angel One SmartAPI
- **Provider**: Angel One Ltd.
- **API Portal**: [smartapi.angelbroking.com](https://smartapi.angelbroking.com/)
- **Cost**: Free API access for active retail demat accounts.
- **Environment Variables**:
  ```env
  ANGEL_ONE_API_KEY=your_api_key
  ANGEL_ONE_CLIENT_CODE=your_client_code
  ANGEL_ONE_PASSWORD=your_password
  ANGEL_ONE_TOTP_KEY=your_totp_secret_key
  ```

---

## 4. API Request Protocol
Whenever the platform encounters a component that lacks its required external credentials, it adheres strictly to the Master Protocol:
```
🔑 API REQUIRED
Component: [component name]
Purpose: [why it is needed]
Provider: [provider]
Required API: [API name]
Required permissions/endpoints: [list]
Free alternative: [yes/no + option]
Paid alternative: [option + approximate cost if known]
Environment variable: [NAME]
Status: WAITING FOR USER
```
No fake or simulated data will masquerade as live broker feeds.

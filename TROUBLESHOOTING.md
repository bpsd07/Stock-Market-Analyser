# Troubleshooting & Diagnostic Runbook

## 1. Common Scenarios

### 1.1 "Connection Refused / Failed to Fetch" on Frontend
- **Cause**: Backend FastAPI server is not running on port 8000.
- **Remedy**: Start backend with `.venv\Scripts\python -m uvicorn backend.api.main:app --port 8000`.

### 1.2 "Yahoo Finance Rate Limiting"
- **Cause**: Rapid consecutive downloads across large stock lists.
- **Remedy**: The built-in LRU/Redis cache stores OHLCV data with a 10-minute TTL. The screener uses concurrency limiting (8 parallel tasks) to stay within public limits.

### 1.3 Missing External API Keys
- **Behavior**: The system gracefully falls back to deterministic analysis and free data. Missing options APIs cleanly return `"status": "NOT_CONFIGURED"`.

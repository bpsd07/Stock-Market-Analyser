# Deployment & Operations Guide

## 1. Local Development (Windows 11 / Modest Laptop)
The system is optimized for a modest 16 GB RAM / integrated GPU machine:
1. Activate virtual environment:
   ```powershell
   .venv\Scripts\activate
   ```
2. Start Backend API:
   ```powershell
   python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
   ```
3. Start Frontend Terminal:
   ```powershell
   cd frontend
   npm run dev
   ```
4. Access Terminal at `http://localhost:3000` and API docs at `http://localhost:8000/docs`.

---

## 2. Docker Compose Production Deployment
```bash
docker compose up -d --build
```
This deploys PostgreSQL, Redis, FastAPI Backend, and Next.js Frontend with automatic health checks.

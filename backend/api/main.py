"""FastAPI Application Entry Point.
Initializes middleware, routers, lifespans, and error handlers.
"""
from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.core.database import init_db
from backend.api.routes import market, scanner, stocks, macro, agents, signals, backtest, paper, system

logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger("trading_platform")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database schema...")
    try:
        await init_db()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.warning(f"Database init warning: {e}")
    yield
    logger.info("Shutting down trading intelligence platform.")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Production-grade AI-powered market intelligence, quantitative screening, and trading platform.",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers under /api/v1
app.include_router(market.router, prefix=settings.API_V1_STR)
app.include_router(scanner.router, prefix=settings.API_V1_STR)
app.include_router(stocks.router, prefix=settings.API_V1_STR)
app.include_router(macro.router, prefix=settings.API_V1_STR)
app.include_router(agents.router, prefix=settings.API_V1_STR)
app.include_router(signals.router, prefix=settings.API_V1_STR)
app.include_router(backtest.router, prefix=settings.API_V1_STR)
app.include_router(paper.router, prefix=settings.API_V1_STR)
app.include_router(system.router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    return {
        "platform": settings.APP_NAME,
        "status": "ONLINE",
        "api_docs": "/docs",
        "mode": settings.EXECUTION_MODE,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.api.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)

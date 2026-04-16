"""
finAG — Main Application
FastAPI server with endpoints for equity research analysis.
"""

import sys
import time
from pathlib import Path
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from config import settings
from models.schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    FinancialData,
    TechnicalAnalysis,
    ReportSummary,
)
from tools.yfinance_tool import (
    fetch_financial_data,
    fetch_price_history,
    financial_data_to_summary,
)
from tools.technical_tool import compute_technical_analysis
from tools.news_tool import fetch_news


# ── Logging Setup ──
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> — {message}",
    level="DEBUG" if settings.DEBUG else "INFO",
)


# ── App Lifecycle ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("=" * 50)
    logger.info("  finAG — AI Equity Research Agent")
    logger.info(f"  LLM Provider: {settings.llm_provider}")
    logger.info(f"  Debug: {settings.DEBUG}")
    logger.info("=" * 50)
    yield
    logger.info("finAG shutting down")


# ── Create App ──
app = FastAPI(
    title="finAG",
    description="AI-powered Equity Research Agent — multi-agent system that generates professional stock analysis reports.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS (allow frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Endpoints ──

@app.get("/")
async def root():
    """Health check."""
    return {
        "app": "finAG",
        "status": "running",
        "version": "0.1.0",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "llm_provider": settings.llm_provider,
        "news_api": "configured" if settings.NEWS_API_KEY else "not configured (using Google News RSS)",
    }


@app.post("/analyze/financial", response_model=FinancialData)
async def analyze_financial(request: AnalyzeRequest):
    """
    Fetch financial data for a ticker.
    Day 1 endpoint — test the yfinance tool directly.
    """
    try:
        data = fetch_financial_data(request.ticker)
        return data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Financial analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.post("/analyze/technical", response_model=TechnicalAnalysis)
async def analyze_technical(request: AnalyzeRequest):
    """
    Run technical analysis on a ticker.
    Returns moving averages, RSI, MACD, trend, etc.
    """
    try:
        result = compute_technical_analysis(request.ticker)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Technical analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/analyze/price-history/{ticker}")
async def get_price_history(ticker: str, period: str = "1y"):
    """
    Fetch price history for charting.
    Periods: 1mo, 3mo, 6mo, 1y, 2y, 5y
    """
    try:
        history = fetch_price_history(ticker, period=period)
        return {"ticker": ticker.upper(), "period": period, "data": history}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/analyze/news/{ticker}")
async def get_news(ticker: str):
    """
    Fetch recent news articles for a ticker.
    Uses NewsAPI if configured, falls back to Google News RSS.
    """
    try:
        # First get company name from yfinance
        financial = fetch_financial_data(ticker)
        articles = fetch_news(financial.company_name, ticker, max_results=10)
        return {
            "ticker": ticker.upper(),
            "company": financial.company_name,
            "article_count": len(articles),
            "articles": articles,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_full(request: AnalyzeRequest):
    """
    Full analysis endpoint (stub for now).
    In Day 7-8, this will trigger the complete CrewAI multi-agent pipeline.
    For now, it runs financial + technical analysis as a preview.
    """
    start = time.time()
    ticker = request.ticker.upper()

    try:
        # Step 1: Financial data
        logger.info(f"[{ticker}] Starting analysis...")
        financial = fetch_financial_data(ticker)

        # Step 2: Technical analysis
        logger.info(f"[{ticker}] Running technical analysis...")
        technical = compute_technical_analysis(ticker)

        # Step 3: News
        logger.info(f"[{ticker}] Fetching news...")
        articles = fetch_news(financial.company_name, ticker, max_results=10)

        elapsed = time.time() - start
        logger.success(f"[{ticker}] Analysis complete in {elapsed:.1f}s")

        # Build a basic summary (will be replaced by CrewAI report agent)
        summary = ReportSummary(
            executive_summary=f"Preliminary analysis of {financial.company_name} ({ticker}). "
                              f"Current price: {financial.currency} {financial.current_price}. "
                              f"Trend: {technical.trend.value}. "
                              f"Found {len(articles)} recent news articles.",
            technical_verdict=technical.analysis_summary,
            sentiment_verdict=f"Collected {len(articles)} news articles for sentiment analysis.",
        )

        return AnalyzeResponse(
            ticker=ticker,
            company_name=financial.company_name,
            status="completed",
            summary=summary,
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"[{ticker}] Analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ── Run ──
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )

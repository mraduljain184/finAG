"""
finAG — Data Models
Pydantic schemas for API requests, responses, and inter-agent data.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class Recommendation(str, Enum):
    STRONG_BUY = "Strong Buy"
    BUY = "Buy"
    HOLD = "Hold"
    SELL = "Sell"
    STRONG_SELL = "Strong Sell"

class SentimentLabel(str, Enum):
    POSITIVE = "Positive"
    NEGATIVE = "Negative"
    NEUTRAL = "Neutral"

class TrendDirection(str, Enum):
    UPTREND = "Uptrend"
    DOWNTREND = "Downtrend"
    SIDEWAYS = "Sideways"

class AnalyzeRequest(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10, examples=["AAPL", "RELIANCE.NS"])

class AnalyzeResponse(BaseModel):
    ticker: str
    company_name: str
    status: str = "completed"
    report_url: Optional[str] = None
    summary: Optional["ReportSummary"] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)

class FinancialData(BaseModel):
    ticker: str
    company_name: str
    sector: str = ""
    industry: str = ""
    market_cap: Optional[float] = None
    current_price: Optional[float] = None
    currency: str = "USD"

    # Valuation
    pe_ratio: Optional[float] = None
    forward_pe: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    peg_ratio: Optional[float] = None

    # Profitability
    revenue: Optional[float] = None
    revenue_growth: Optional[float] = None
    net_income: Optional[float] = None
    profit_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    roe: Optional[float] = None

    # Per share
    eps: Optional[float] = None
    dividend_yield: Optional[float] = None

    # Health
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    free_cash_flow: Optional[float] = None

    # Range
    week_52_high: Optional[float] = None
    week_52_low: Optional[float] = None
    avg_volume: Optional[float] = None
    beta: Optional[float] = None

class NewsArticle(BaseModel):
    title: str
    source: str = ""
    url: str = ""
    published_at: str = ""
    summary: str = ""
    sentiment: SentimentLabel = SentimentLabel.NEUTRAL
    sentiment_score: float = 0.0

class NewsSentiment(BaseModel):
    ticker: str
    overall_sentiment: SentimentLabel = SentimentLabel.NEUTRAL
    overall_score: float = 0.0
    positive_count: int = 0
    negative_count: int = 0
    neutral_count: int = 0
    articles: list[NewsArticle] = []
    analysis_summary: str = ""

class CompetitorMetrics(BaseModel):
    ticker: str
    company_name: str
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    revenue_growth: Optional[float] = None
    profit_margin: Optional[float] = None
    current_price: Optional[float] = None


class CompetitorAnalysis(BaseModel):
    target_ticker: str
    sector: str = ""
    competitors: list[CompetitorMetrics] = []
    competitive_position: str = ""
    moat_assessment: str = ""

class TechnicalAnalysis(BaseModel):
    ticker: str
    current_price: Optional[float] = None

    sma_50: Optional[float] = None
    sma_200: Optional[float] = None
    ema_20: Optional[float] = None

    rsi_14: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None

    support_level: Optional[float] = None
    resistance_level: Optional[float] = None

    trend: TrendDirection = TrendDirection.SIDEWAYS
    golden_cross: bool = False
    death_cross: bool = False

    analysis_summary: str = ""

class ReportSummary(BaseModel):
    recommendation: Recommendation = Recommendation.HOLD
    target_price: Optional[float] = None
    confidence: float = 0.0
    executive_summary: str = ""
    key_strengths: list[str] = []
    key_risks: list[str] = []
    sentiment_verdict: str = ""
    technical_verdict: str = ""

AnalyzeResponse.model_rebuild()
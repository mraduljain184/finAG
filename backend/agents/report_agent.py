"""
finAG — Report Writer Agent
Synthesizes outputs from all specialist agents into a final equity research report.
Acts as a Chief Investment Officer making the final Buy/Hold/Sell decision.
"""

import json
import re
from loguru import logger
from tools.llm_tool import ask_llm, ask_llm_json
from models.schemas import (
    FinancialData,
    NewsSentiment,
    CompetitorAnalysis,
    TechnicalAnalysis,
    ReportSummary,
    Recommendation,
)


REPORT_AGENT_SYSTEM_PROMPT = """You are the Chief Investment Officer at a premier equity research firm.
Your job is to synthesize analyses from 4 specialist analysts (fundamental, sentiment, technical, competitive) 
and produce a FINAL investment recommendation.

You must:
1. Weigh the evidence from all 4 analyses.
2. Identify where analyses agree (strong signals) and where they conflict (caution).
3. Produce a clear recommendation: Strong Buy, Buy, Hold, Sell, or Strong Sell.
4. Provide a realistic 12-month target price with justification.
5. Give a confidence score (0-100%) based on how much the signals agree.
6. List the top 3 key strengths and top 3 key risks.

Framework for recommendation:
- STRONG BUY: All 4 analyses positive, strong fundamentals + positive sentiment + bullish technicals + competitive moat
- BUY: Mostly positive signals, minor concerns acceptable
- HOLD: Mixed signals, fairly valued, no clear catalyst either way
- SELL: Mostly negative signals, better opportunities elsewhere
- STRONG SELL: All 4 analyses negative, deteriorating fundamentals + negative sentiment + bearish technicals

Rules:
- Be decisive. "Hold" should be used when genuinely mixed, not as a cop-out.
- Your target price must be justifiable — reference current price, P/E multiples, or recent trading range.
- Confidence = agreement between analyses. If all 4 agree, confidence should be 75-90%. If they conflict, 40-60%.
- The executive summary should be 3-4 sentences suitable for a hedge fund CIO who only has 30 seconds.
"""

REPORT_JSON_STRUCTURE = """Return your analysis in this EXACT JSON structure:
{
    "recommendation": "Strong Buy" | "Buy" | "Hold" | "Sell" | "Strong Sell",
    "target_price": <number>,
    "confidence": <number 0-100>,
    "executive_summary": "3-4 sentence high-level summary for a CIO",
    "key_strengths": ["strength 1", "strength 2", "strength 3"],
    "key_risks": ["risk 1", "risk 2", "risk 3"],
    "sentiment_verdict": "1-2 sentence take on news sentiment",
    "technical_verdict": "1-2 sentence take on technicals",
    "fundamental_verdict": "1-2 sentence take on fundamentals",
    "competitive_verdict": "1-2 sentence take on competitive positioning"
}
"""

def run_report_agent(
    ticker: str,
    company_name: str,
    financial_data: FinancialData,
    financial_analysis: str,
    news_sentiment: NewsSentiment,
    technical_data: TechnicalAnalysis,
    technical_analysis: str,
    competitor_analysis: CompetitorAnalysis,
) -> ReportSummary:
    """
    Synthesize all agent outputs into a final report.

    Args:
        ticker: Stock ticker
        company_name: Company name
        financial_data: Raw financial data
        financial_analysis: LLM analysis from financial agent
        news_sentiment: Output from news agent
        technical_data: Raw technical indicators
        technical_analysis: LLM analysis from technical agent
        competitor_analysis: Output from competitor agent

    Returns:
        ReportSummary with final recommendation, target price, confidence, etc.
    """
    logger.info(f"[Report Agent] Synthesizing final report for {ticker}")

    # Build a rich context combining all analyses
    context = f"""
=== EQUITY RESEARCH SYNTHESIS: {company_name} ({ticker}) ===

Current Price: {financial_data.currency} {financial_data.current_price}
Market Cap: {financial_data.market_cap}
Sector: {financial_data.sector}

══════════════════════════════════════════════════
SPECIALIST ANALYSIS #1 — FUNDAMENTAL (Financial Agent)
══════════════════════════════════════════════════
{financial_analysis}

══════════════════════════════════════════════════
SPECIALIST ANALYSIS #2 — NEWS SENTIMENT (News Agent)
══════════════════════════════════════════════════
Overall Sentiment: {news_sentiment.overall_sentiment.value} (Score: {news_sentiment.overall_score})
Article Breakdown: {news_sentiment.positive_count} positive, {news_sentiment.negative_count} negative, {news_sentiment.neutral_count} neutral

Sentiment Summary:
{news_sentiment.analysis_summary}

══════════════════════════════════════════════════
SPECIALIST ANALYSIS #3 — TECHNICAL (Technical Agent)
══════════════════════════════════════════════════
Trend: {technical_data.trend.value}
RSI: {technical_data.rsi_14} | MACD Histogram: {technical_data.macd_histogram}
Support: ${technical_data.support_level} | Resistance: ${technical_data.resistance_level}

Technical Analysis:
{technical_analysis}

══════════════════════════════════════════════════
SPECIALIST ANALYSIS #4 — COMPETITIVE (Competitor Agent)
══════════════════════════════════════════════════
Competitors Analyzed: {len(competitor_analysis.competitors)}
Peer Tickers: {', '.join(c.ticker for c in competitor_analysis.competitors)}

Competitive Analysis:
{competitor_analysis.competitive_position}
"""
    
    # Ask LLM to synthesize
    prompt = f"""{context}

═══════════════════════════════════════════════════
YOUR TASK
═══════════════════════════════════════════════════
Based on ALL 4 specialist analyses above, produce your final investment recommendation.

{REPORT_JSON_STRUCTURE}

Remember:
- The target_price should be a realistic 12-month projection (not random).
- Confidence reflects agreement between the 4 analyses.
- key_strengths and key_risks should each have exactly 3 items.
- Be decisive in your recommendation.
"""

    try:
        response = ask_llm_json(prompt, system_prompt=REPORT_AGENT_SYSTEM_PROMPT, max_tokens=2500)

        # Clean the response
        response = response.strip()
        response = re.sub(r"^```json?\s*", "", response)
        response = re.sub(r"\s*```$", "", response)

        data = json.loads(response)

        # Map recommendation string to enum
        try:
            recommendation = Recommendation(data.get("recommendation", "Hold"))
        except ValueError:
            recommendation = Recommendation.HOLD

        result = ReportSummary(
            recommendation=recommendation,
            target_price=float(data.get("target_price", 0.0)) if data.get("target_price") else None,
            confidence=float(data.get("confidence", 50.0)),
            executive_summary=data.get("executive_summary", ""),
            key_strengths=data.get("key_strengths", [])[:3],
            key_risks=data.get("key_risks", [])[:3],
            sentiment_verdict=data.get("sentiment_verdict", ""),
            technical_verdict=data.get("technical_verdict", ""),
        )

        logger.success(
            f"[Report Agent] Final recommendation for {ticker}: {recommendation.value} "
            f"(target: ${result.target_price}, confidence: {result.confidence}%)"
        )

        return result
    except Exception as e:
        logger.error(f"[Report Agent] Synthesis failed: {e}")
        # Fallback: return a minimal report
        return ReportSummary(
            recommendation=Recommendation.HOLD,
            confidence=0.0,
            executive_summary=f"Unable to generate full synthesis for {ticker}. Raw specialist analyses are available.",
            key_strengths=[],
            key_risks=[],
        )
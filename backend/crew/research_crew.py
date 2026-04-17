"""
finAG — Research Crew Orchestrator
Runs all 5 agents in sequence to produce a complete equity research report.
This is the main pipeline that chains the specialist agents together.
"""

import time
from loguru import logger

from agents.financial_agent import run_financial_agent
from agents.news_agent import run_news_agent
from agents.technical_agent import run_technical_agent
from agents.competitor_agent import run_competitor_agent
from agents.report_agent import run_report_agent


def run_research_crew(ticker: str) -> dict:
    """
    Run the full multi-agent research pipeline.

    Pipeline:
    1. Financial agent — fundamental analysis
    2. News sentiment agent — market sentiment
    3. Technical agent — chart/momentum analysis
    4. Competitor agent — peer comparison
    5. Report agent — synthesizes all of the above

    Args:
        ticker: Stock ticker symbol

    Returns:
        Complete research output with raw data, all specialist analyses, and final report
    """
    ticker = ticker.upper()
    logger.info(f"═══════════════════════════════════════════════════")
    logger.info(f"  FIN RESEARCH CREW — Starting analysis for {ticker}")
    logger.info(f"═══════════════════════════════════════════════════")

    start_time = time.time()

    # ── Step 1: Financial Agent ──
    logger.info(f"[Crew] Step 1/5: Running Financial Agent...")
    step_start = time.time()
    financial_result = run_financial_agent(ticker)
    logger.info(f"[Crew] Step 1 done in {time.time() - step_start:.1f}s")

    # ── Step 2: News Sentiment Agent ──
    logger.info(f"[Crew] Step 2/5: Running News Sentiment Agent...")
    step_start = time.time()
    news_result = run_news_agent(ticker)
    logger.info(f"[Crew] Step 2 done in {time.time() - step_start:.1f}s")

    # ── Step 3: Technical Agent ──
    logger.info(f"[Crew] Step 3/5: Running Technical Agent...")
    step_start = time.time()
    technical_result = run_technical_agent(ticker)
    logger.info(f"[Crew] Step 3 done in {time.time() - step_start:.1f}s")

    # ── Step 4: Competitor Agent ──
    logger.info(f"[Crew] Step 4/5: Running Competitor Agent...")
    step_start = time.time()
    competitor_result = run_competitor_agent(ticker)
    logger.info(f"[Crew] Step 4 done in {time.time() - step_start:.1f}s")

    # ── Step 5: Report Synthesis ──
    logger.info(f"[Crew] Step 5/5: Running Report Writer Agent (synthesizing all)...")
    step_start = time.time()
    final_report = run_report_agent(
        ticker=ticker,
        company_name=financial_result["data"].company_name,
        financial_data=financial_result["data"],
        financial_analysis=financial_result["analysis"],
        news_sentiment=news_result,
        technical_data=technical_result["data"],
        technical_analysis=technical_result["analysis"],
        competitor_analysis=competitor_result,
    )
    logger.info(f"[Crew] Step 5 done in {time.time() - step_start:.1f}s")


    total_time = time.time() - start_time
    logger.success(f"═══════════════════════════════════════════════════")
    logger.success(f"  CREW COMPLETE — {ticker}: {final_report.recommendation.value}")
    logger.success(f"  Total time: {total_time:.1f}s")
    logger.success(f"═══════════════════════════════════════════════════")

    return {
        "ticker": ticker,
        "company_name": financial_result["data"].company_name,
        "generated_at": time.time(),
        "total_time_seconds": round(total_time, 1),

        # Final synthesized report
        "report": final_report.model_dump(),

        # All specialist outputs (for transparency)
        "financial": {
            "data": financial_result["data"].model_dump(),
            "analysis": financial_result["analysis"],
        },
        "news_sentiment": news_result.model_dump(),
        "technical": {
            "data": technical_result["data"].model_dump(),
            "analysis": technical_result["analysis"],
        },
        "competitor": competitor_result.model_dump(),
    }
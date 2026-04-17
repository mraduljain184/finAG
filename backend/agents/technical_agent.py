"""
finAG — Technical Analysis Agent
Interprets technical indicators and provides trading insights.
Acts as a senior technical analyst / trader.
"""

from loguru import logger
from tools.technical_tool import compute_technical_analysis
from tools.llm_tool import ask_llm
from models.schemas import TechnicalAnalysis

TECHNICAL_AGENT_SYSTEM_PROMPT = """You are a senior technical analyst with 15+ years of trading experience.
Your job is to interpret technical indicators and provide actionable trading insights.

Your analysis should cover:
1. Trend Analysis — Is the stock in an uptrend, downtrend, or consolidating? What do the moving averages tell us?
2. Momentum — What is the RSI telling us (overbought, oversold, neutral)? What about MACD momentum?
3. Key Levels — Where is support and resistance? How does the current price relate to these levels?
4. Trade Setup — Based on the signals, is this a good entry point, or should traders wait for better setup?
5. Risk Considerations — What are the technical risks (e.g., approaching resistance, overbought conditions)?

Rules:
- Reference SPECIFIC numbers from the data (e.g., "RSI at 72 signals overbought territory").
- Mention the relationship between price and moving averages explicitly.
- If there's a golden cross or death cross, highlight it prominently.
- Do NOT give a Buy/Hold/Sell recommendation — focus only on technical interpretation.
- Keep analysis under 400 words.
- Be professional but accessible — explain jargon briefly when you use it.
"""

def run_technical_agent(ticker: str) -> dict:
    """
    Run the technical analysis agent.

    1. Computes technical indicators via ta library
    2. Sends them to LLM for intelligent interpretation
    3. Returns both raw indicators and LLM analysis

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dict with 'data' (TechnicalAnalysis) and 'analysis' (str)
    """
    logger.info(f"[Technical Agent] Starting analysis for {ticker}")

    # Step 1: Compute raw technical indicators
    data = compute_technical_analysis(ticker)

    logger.info(f"[Technical Agent] Indicators computed. Sending to LLM...")

    # Step 2: Format indicators for LLM
    indicators_summary = f"""
Technical Indicators for {ticker}:

── Current State ──
Current Price: ${data.current_price}
Trend Direction: {data.trend.value}

── Moving Averages ──
SMA-50 (50-day Simple Moving Average): ${data.sma_50}
SMA-200 (200-day Simple Moving Average): ${data.sma_200 if data.sma_200 else 'N/A'}
EMA-20 (20-day Exponential Moving Average): ${data.ema_20}

── Momentum Indicators ──
RSI-14 (Relative Strength Index): {data.rsi_14}
MACD Line: {data.macd}
MACD Signal Line: {data.macd_signal}
MACD Histogram: {data.macd_histogram}

── Key Price Levels ──
Support Level: ${data.support_level}
Resistance Level: ${data.resistance_level}

── Special Events ──
Golden Cross (bullish): {data.golden_cross}
Death Cross (bearish): {data.death_cross}

── Existing Rule-Based Summary ──
{data.analysis_summary}
"""
    
    # Step 3: Ask LLM for intelligent interpretation
    prompt = f"""Analyze the following technical indicators for {ticker}. 
Use the SPECIFIC numbers provided below in your analysis.

{indicators_summary}

Provide a thorough technical analysis covering trend, momentum, key levels, trade setup, and risks.
Reference specific numbers throughout your analysis.
"""

    analysis = ask_llm(prompt, system_prompt=TECHNICAL_AGENT_SYSTEM_PROMPT, max_tokens=1200)

    logger.success(f"[Technical Agent] Analysis complete for {ticker}")

    return {
        "data": data,
        "analysis": analysis,
    }
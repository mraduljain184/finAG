"""
finAG — Financial Data Agent
Takes raw financial data and produces intelligent fundamental analysis.
Acts as a senior equity research analyst.
"""

from loguru import logger
from tools.yfinance_tool import fetch_financial_data, financial_data_to_summary
from tools.llm_tool import ask_llm
from models.schemas import FinancialData

FINANCIAL_AGENT_SYSTEM_PROMPT = """You are a senior equity research analyst at a top-tier investment bank.
Your job is to analyze fundamental financial data and provide clear, professional assessments.

Your analysis should cover:
1. Valuation Assessment — Is the stock overvalued, undervalued, or fairly valued? Compare P/E, P/B, P/S ratios against typical ranges for the sector.
2. Profitability Analysis — How strong are the margins? Is revenue growing? How efficient is the company (ROE)?
3. Financial Health — Is the balance sheet strong? How is the debt situation? Is there enough free cash flow?
4. Key Strengths — What stands out positively?
5. Key Risks — What are the red flags or concerns?

Rules:
- Be specific with numbers. Don't say "good margins" — say "profit margin of 27% is well above the sector average of ~15%".
- Be balanced. Every stock has both strengths and risks.
- Write in a professional but accessible tone.
- Keep the total analysis under 500 words.
- Do NOT give a Buy/Hold/Sell recommendation — that comes later from the report synthesis agent.
"""

def run_financial_agent(ticker: str) -> dict:
    """
    Run the financial data agent.

    1. Fetches financial data from yfinance
    2. Sends it to Claude for intelligent analysis
    3. Returns both raw data and LLM analysis

    Args:
        ticker: Stock ticker symbol

    Returns:
        Dict with 'data' (FinancialData) and 'analysis' (str)
    """
    logger.info(f"[Financial Agent] Starting analysis for {ticker}")

    # Step 1: Fetch raw financial data
    data = fetch_financial_data(ticker)
    summary = financial_data_to_summary(data)

    logger.info(f"[Financial Agent] Data fetched for {data.company_name}. Sending to LLM...")

    # Step 2: Ask Claude to analyze the data
    prompt = f"""Below is the complete financial data for {data.company_name} ({ticker}). 
Read EVERY metric carefully — all data you need is included below.

{summary}

Now provide your analysis. You must reference the SPECIFIC numbers from the data above 
(profit margin, revenue growth, ROE, debt-to-equity, free cash flow, etc.) in your analysis. 
Do NOT say "data not provided" — every key metric is in the summary above.
"""

    analysis = ask_llm(prompt, system_prompt=FINANCIAL_AGENT_SYSTEM_PROMPT)

    logger.success(f"[Financial Agent] Analysis complete for {ticker}")

    return {
        "data": data,
        "analysis": analysis,
    }
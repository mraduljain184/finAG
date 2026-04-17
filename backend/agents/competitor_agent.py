"""
finAG — Competitor Analysis Agent
Identifies competitors, fetches their financials, and writes comparative analysis.
Acts as a market analyst focused on competitive positioning.
"""

import json
import re
from loguru import logger
from tools.yfinance_tool import fetch_financial_data
from tools.llm_tool import ask_llm, ask_llm_json
from models.schemas import CompetitorAnalysis, CompetitorMetrics

COMPETITOR_IDENTIFY_PROMPT = """You are a market research analyst specialized in competitive analysis.
Given a company's name and industry, identify its TOP 3-4 direct competitors that are publicly traded.

Rules:
- Return ONLY publicly traded companies with US stock tickers (for international companies, use their ADR ticker if available)
- Focus on direct competitors in the same product/service space, not tangential players
- Prefer well-known, large-cap competitors over obscure ones
- Do NOT include the original company in the list

Return a JSON array of ticker symbols only. Example format:
["MSFT", "GOOGL", "META", "AMZN"]
"""

COMPETITOR_ANALYSIS_PROMPT = """You are a senior equity research analyst focused on competitive positioning.
Your job is to analyze how a company stacks up against its main competitors.

Your analysis should cover:
1. Market Position — Where does this company rank vs peers in size (market cap), growth, and profitability?
2. Valuation Comparison — Is this company trading at a premium or discount to peers? Why might that be?
3. Competitive Strengths — Based on the metrics, what does this company do better than peers?
4. Competitive Weaknesses — Where is this company lagging vs peers?
5. Moat Assessment — Does this company have a defensible competitive advantage (moat)?

Rules:
- Reference SPECIFIC numbers when comparing (e.g., "Apple's 27% profit margin exceeds Samsung's 14%").
- Be balanced — identify both strengths and weaknesses.
- Keep the analysis under 500 words.
- Do NOT give Buy/Sell recommendations.
"""


def identify_competitors(company_name: str, ticker: str, sector: str, industry: str) -> list[str]:
    """
    Use LLM to identify 3-4 direct competitors.
    Returns a list of ticker symbols.
    """
    logger.info(f"[Competitor Agent] Identifying competitors for {company_name}")

    prompt = f"""Identify the top 3-4 publicly traded competitors for:

Company: {company_name} ({ticker})
Sector: {sector}
Industry: {industry}

Return a JSON array of ticker symbols only.
"""

    try:
        response = ask_llm_json(prompt, system_prompt=COMPETITOR_IDENTIFY_PROMPT, max_tokens=200)

        # Clean the response
        response = response.strip()
        # Remove markdown code blocks if present
        response = re.sub(r"^```json?\s*", "", response)
        response = re.sub(r"\s*```$", "", response)

        tickers = json.loads(response)

        # Validate it's a list of strings
        if not isinstance(tickers, list):
            raise ValueError("Response is not a list")

        # Filter out the original ticker if LLM accidentally included it
        tickers = [t.upper() for t in tickers if t.upper() != ticker.upper()]

        logger.success(f"[Competitor Agent] Identified: {tickers}")
        return tickers[:4]  # Max 4 competitors

    except Exception as e:
        logger.warning(f"[Competitor Agent] Failed to identify competitors via LLM: {e}")
        return []
    

def run_competitor_agent(ticker: str) -> CompetitorAnalysis:
    """
    Run the competitor analysis agent.

    1. Fetches target company data
    2. Uses LLM to identify competitors
    3. Fetches competitor financial data
    4. Uses LLM to write comparative analysis

    Args:
        ticker: Stock ticker symbol

    Returns:
        CompetitorAnalysis with competitor metrics and analysis
    """
    logger.info(f"[Competitor Agent] Starting analysis for {ticker}")

    # Step 1: Fetch target company data
    target = fetch_financial_data(ticker)

    # Step 2: Identify competitors
    competitor_tickers = identify_competitors(
        company_name=target.company_name,
        ticker=ticker,
        sector=target.sector,
        industry=target.industry,
    )

    if not competitor_tickers:
        logger.warning(f"[Competitor Agent] No competitors identified, returning minimal result")
        return CompetitorAnalysis(
            target_ticker=ticker.upper(),
            sector=target.sector,
            competitive_position="Could not identify competitors for comparison.",
            moat_assessment="Insufficient comparative data.",
        )
    
    # Step 3: Fetch competitor financial data
    competitor_metrics = []
    for comp_ticker in competitor_tickers:
        try:
            comp_data = fetch_financial_data(comp_ticker)
            competitor_metrics.append(CompetitorMetrics(
                ticker=comp_data.ticker,
                company_name=comp_data.company_name,
                market_cap=comp_data.market_cap,
                pe_ratio=comp_data.pe_ratio,
                revenue_growth=comp_data.revenue_growth,
                profit_margin=comp_data.profit_margin,
                current_price=comp_data.current_price,
            ))
            logger.info(f"[Competitor Agent] Fetched {comp_ticker}: {comp_data.company_name}")
        except Exception as e:
            logger.warning(f"[Competitor Agent] Failed to fetch {comp_ticker}: {e}")
            continue

    
    # Step 4: Format data for LLM comparison
    def format_for_llm(t: str, name: str, mc, pe, rg, pm):
        mc_str = f"${mc / 1e9:.1f}B" if mc else "N/A"
        pe_str = f"{pe:.1f}" if pe else "N/A"
        rg_str = f"{rg * 100:.1f}%" if rg else "N/A"
        pm_str = f"{pm * 100:.1f}%" if pm else "N/A"
        return f"{name} ({t}): Market Cap {mc_str} | P/E {pe_str} | Revenue Growth {rg_str} | Profit Margin {pm_str}"

    target_line = format_for_llm(
        target.ticker, target.company_name, target.market_cap,
        target.pe_ratio, target.revenue_growth, target.profit_margin
    )

    competitor_lines = [
        format_for_llm(c.ticker, c.company_name, c.market_cap, c.pe_ratio, c.revenue_growth, c.profit_margin)
        for c in competitor_metrics
    ]

    comparison_text = f"""
TARGET COMPANY:
{target_line}

COMPETITORS:
{chr(10).join(competitor_lines)}
"""
    
    # Step 5: Ask LLM for comparative analysis
    prompt = f"""Compare {target.company_name} ({ticker}) against its direct competitors using the data below.

{comparison_text}

Provide a thorough competitive analysis covering market position, valuation, strengths, weaknesses, and moat.
Reference specific numbers from the comparison above.
"""

    analysis = ask_llm(prompt, system_prompt=COMPETITOR_ANALYSIS_PROMPT, max_tokens=1500)

    # Step 6: Build result
    result = CompetitorAnalysis(
        target_ticker=ticker.upper(),
        sector=target.sector,
        competitors=competitor_metrics,
        competitive_position=analysis,
        moat_assessment="",  # Will be filled by report synthesis later
    )

    logger.success(f"[Competitor Agent] Analysis complete for {ticker} vs {len(competitor_metrics)} peers")

    return result
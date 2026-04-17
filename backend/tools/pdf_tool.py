"""
finAG — PDF Generator Tool
Converts the final research JSON into a professional PDF report.
Uses Jinja2 for templating and WeasyPrint for HTML-to-PDF conversion.
"""

import os
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from loguru import logger

# Setup Jinja2 environment
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))

# Helper formatters
def _fmt_num(num):
    """Format large numbers: 1.5T, 234.5B, 12.3M."""
    if num is None:
        return "N/A"
    abs_num = abs(num)
    sign = "-" if num < 0 else ""
    if abs_num >= 1_000_000_000_000:
        return f"{sign}${abs_num / 1_000_000_000_000:.2f}T"
    elif abs_num >= 1_000_000_000:
        return f"{sign}${abs_num / 1_000_000_000:.2f}B"
    elif abs_num >= 1_000_000:
        return f"{sign}${abs_num / 1_000_000:.2f}M"
    return f"{sign}${abs_num:,.2f}"


def _fmt_pct(val):
    """Format decimal as percentage."""
    if val is None:
        return "N/A"
    return f"{val * 100:.2f}%"


def _fmt_float(val, decimals=2):
    """Format a float safely."""
    if val is None:
        return "N/A"
    return f"{val:.{decimals}f}"

def _get_rec_class(recommendation: str) -> str:
    """Map recommendation to CSS class."""
    mapping = {
        "Strong Buy": "strong-buy",
        "Buy": "buy",
        "Hold": "hold",
        "Sell": "sell",
        "Strong Sell": "strong-sell",
    }
    return mapping.get(recommendation, "hold")


def _get_sentiment_class(sentiment: str) -> str:
    """Map sentiment label to CSS class."""
    return sentiment.lower() if sentiment in ["Positive", "Negative", "Neutral"] else "neutral"

def generate_pdf_report(research_data: dict, output_path: str = None) -> str:
    """
    Generate a PDF report from the crew output.

    Args:
        research_data: The dict returned by run_research_crew()
        output_path: Where to save the PDF. Defaults to reports/{TICKER}_{timestamp}.pdf

    Returns:
        Path to the generated PDF file.
    """
    ticker = research_data["ticker"]
    logger.info(f"[PDF] Generating report for {ticker}")

    # Default output path
    if output_path is None:
        reports_dir = Path(__file__).resolve().parent.parent.parent / "reports"
        reports_dir.mkdir(exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        output_path = str(reports_dir / f"{ticker}_{timestamp}.pdf")

        # Unpack the data
    financial = research_data["financial"]["data"]
    financial_analysis = research_data["financial"]["analysis"]
    technical = research_data["technical"]["data"]
    technical_analysis = research_data["technical"]["analysis"]
    news = research_data["news_sentiment"]
    competitor = research_data["competitor"]
    report = research_data["report"]

    # Prepare context for template
    current_price = financial.get("current_price") or 0
    target_price = report.get("target_price") or current_price
    upside_pct = ((target_price - current_price) / current_price * 100) if current_price else 0

    context = {
        "ticker": ticker,
        "company_name": research_data["company_name"],
        "sector": financial.get("sector", ""),
        "industry": financial.get("industry", ""),
        "generated_at": datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC"),

        # Recommendation
        "recommendation": report.get("recommendation", "Hold"),
        "rec_class": _get_rec_class(report.get("recommendation", "Hold")),
        "current_price": _fmt_float(current_price),
        "target_price": _fmt_float(target_price),
        "upside_pct": f"{upside_pct:+.1f}",
        "confidence": _fmt_float(report.get("confidence", 0), 0),
        "currency": financial.get("currency", "USD"),

        # Summary
        "executive_summary": report.get("executive_summary", ""),
        "key_strengths": report.get("key_strengths", []),
        "key_risks": report.get("key_risks", []),

        # Financial metrics
        "market_cap": _fmt_num(financial.get("market_cap")),
        "pe_ratio": _fmt_float(financial.get("pe_ratio")),
        "forward_pe": _fmt_float(financial.get("forward_pe")),
        "pb_ratio": _fmt_float(financial.get("pb_ratio")),
        "ps_ratio": _fmt_float(financial.get("ps_ratio")),
        "peg_ratio": _fmt_float(financial.get("peg_ratio")),
        "revenue": _fmt_num(financial.get("revenue")),
        "revenue_growth": _fmt_pct(financial.get("revenue_growth")),
        "profit_margin": _fmt_pct(financial.get("profit_margin")),
        "operating_margin": _fmt_pct(financial.get("operating_margin")),
        "roe": _fmt_pct(financial.get("roe")),
        "eps": _fmt_float(financial.get("eps")),
        "financial_analysis": financial_analysis,

        # Technical
        "trend": technical.get("trend", "Unknown"),
        "sma_50": _fmt_float(technical.get("sma_50")),
        "sma_200": _fmt_float(technical.get("sma_200")),
        "ema_20": _fmt_float(technical.get("ema_20")),
        "rsi_14": _fmt_float(technical.get("rsi_14")),
        "macd_histogram": _fmt_float(technical.get("macd_histogram"), 4),
        "support_level": _fmt_float(technical.get("support_level")),
        "resistance_level": _fmt_float(technical.get("resistance_level")),
        "week_52_high": _fmt_float(financial.get("week_52_high")),
        "week_52_low": _fmt_float(financial.get("week_52_low")),
        "golden_cross": "Yes" if technical.get("golden_cross") else "No",
        "death_cross": "Yes" if technical.get("death_cross") else "No",
        "technical_analysis": technical_analysis,

        # Competitors
        "competitors": [
            {
                "ticker": c.get("ticker"),
                "company_name": c.get("company_name"),
                "market_cap": _fmt_num(c.get("market_cap")),
                "pe_ratio": _fmt_float(c.get("pe_ratio")),
                "revenue_growth": _fmt_pct(c.get("revenue_growth")),
                "profit_margin": _fmt_pct(c.get("profit_margin")),
            }
            for c in competitor.get("competitors", [])
        ],
        "competitor_analysis": competitor.get("competitive_position", ""),

        # News
        "overall_sentiment": news.get("overall_sentiment", "Neutral"),
        "positive_count": news.get("positive_count", 0),
        "negative_count": news.get("negative_count", 0),
        "neutral_count": news.get("neutral_count", 0),
        "sentiment_summary": news.get("analysis_summary", ""),
        "articles": [
            {
                "title": a.get("title", ""),
                "source": a.get("source", ""),
                "published_at": a.get("published_at", "")[:10],  # Just date
                "summary": a.get("summary", ""),
                "sentiment_class": _get_sentiment_class(a.get("sentiment", "Neutral")),
            }
            for a in news.get("articles", [])[:10]
        ],
    }

    # Render HTML from template
    template = jinja_env.get_template("report_template.html")
    html_content = template.render(**context)

    # Convert HTML to PDF
    logger.info(f"[PDF] Converting HTML to PDF...")
    HTML(string=html_content).write_pdf(output_path)

    logger.success(f"[PDF] Report generated: {output_path}")
    return output_path
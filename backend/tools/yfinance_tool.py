"""
finAG — yfinance Tool
Fetches comprehensive financial data for any stock ticker.
This is the primary data source for the financial data agent.
"""

import yfinance as yf
from loguru import logger
from models.schemas import FinancialData

def _safe_get(info: dict, key: str, default=None):
    """Safely get a value from yfinance info dict."""
    val = info.get(key, default)
    if val is None or val == "":
        return default
    return val

def fetch_financial_data(ticker: str) -> FinancialData:
    """
    Fetch complete financial data for a stock ticker.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL", "RELIANCE.NS")

    Returns:
        FinancialData object with all available metrics.

    Raises:
        ValueError: If ticker is invalid or data cannot be fetched.
    """
    logger.info(f"Fetching financial data for {ticker}")

    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        if not info or info.get("regularMarketPrice") is None:
            fast = stock.fast_info
            if not hasattr(fast, "last_price") or fast.last_price is None:
                raise ValueError(f"No data found for ticker: {ticker}")

    except ValueError:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch data for {ticker}: {e}")
        raise ValueError(
            f"Ticker '{ticker.upper()}' not found or has no data available. "
            f"Try a valid symbol like AAPL, MSFT, GOOGL, TSLA, NVDA, or RELIANCE.NS for Indian stocks."
        ) from e
    
    data = FinancialData(
        ticker=ticker.upper(),
        company_name=_safe_get(info, "longName", _safe_get(info, "shortName", ticker)),
        sector=_safe_get(info, "sector", ""),
        industry=_safe_get(info, "industry", ""),
        market_cap=_safe_get(info, "marketCap"),
        current_price=_safe_get(info, "currentPrice", _safe_get(info, "regularMarketPrice")),
        currency=_safe_get(info, "currency", "USD"),

        # Valuation
        pe_ratio=_safe_get(info, "trailingPE"),
        forward_pe=_safe_get(info, "forwardPE"),
        pb_ratio=_safe_get(info, "priceToBook"),
        ps_ratio=_safe_get(info, "priceToSalesTrailing12Months"),
        peg_ratio=_safe_get(info, "pegRatio"),

        # Profitability
        revenue=_safe_get(info, "totalRevenue"),
        revenue_growth=_safe_get(info, "revenueGrowth"),
        net_income=_safe_get(info, "netIncomeToCommon"),
        profit_margin=_safe_get(info, "profitMargins"),
        operating_margin=_safe_get(info, "operatingMargins"),
        roe=_safe_get(info, "returnOnEquity"),

        # Per share
        eps=_safe_get(info, "trailingEps"),
        dividend_yield=_safe_get(info, "dividendYield"),

        # Health
        debt_to_equity=_safe_get(info, "debtToEquity"),
        current_ratio=_safe_get(info, "currentRatio"),
        free_cash_flow=_safe_get(info, "freeCashflow"),

        # Range
        week_52_high=_safe_get(info, "fiftyTwoWeekHigh"),
        week_52_low=_safe_get(info, "fiftyTwoWeekLow"),
        avg_volume=_safe_get(info, "averageVolume"),
        beta=_safe_get(info, "beta"),
    )

    logger.success(f"Fetched data for {data.company_name} ({ticker})")
    return data

def fetch_price_history(ticker: str, period: str = "1y") -> dict:
    """
    Fetch historical price data for technical analysis.

    Args:
        ticker: Stock ticker symbol.
        period: Time period — "1mo", "3mo", "6mo", "1y", "2y", "5y".

    Returns:
        Dict with 'dates', 'open', 'high', 'low', 'close', 'volume' lists.
    """
    logger.info(f"Fetching {period} price history for {ticker}")

    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)

    if hist.empty:
        raise ValueError(f"No price history found for ticker: {ticker}")
    
    return {
        "dates": hist.index.strftime("%Y-%m-%d").tolist(),
        "open": hist["Open"].round(2).tolist(),
        "high": hist["High"].round(2).tolist(),
        "low": hist["Low"].round(2).tolist(),
        "close": hist["Close"].round(2).tolist(),
        "volume": hist["Volume"].tolist(),
    }

def fetch_competitor_tickers(ticker: str) -> list[str]:
    """
    Attempt to get peer/competitor tickers from yfinance.
    Falls back to empty list if not available.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            "sector": _safe_get(info, "sector", ""),
            "industry": _safe_get(info, "industry", ""),
        }
    except Exception:
        return {"sector": "", "industry": ""}
    
def format_large_number(num: float | None) -> str:
    """Format large numbers for display: 1.5T, 234.5B, 12.3M, etc."""
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
    elif abs_num >= 1_000:
        return f"{sign}${abs_num / 1_000:.2f}K"
    return f"{sign}${abs_num:.2f}"

def format_percentage(val: float | None) -> str:
    """Format a decimal ratio as percentage string."""
    if val is None:
        return "N/A"
    return f"{val * 100:.2f}%"

def financial_data_to_summary(data: FinancialData) -> str:
    """
    Convert FinancialData to a human-readable summary string.
    Used as input context for other agents.
    """
    return f"""
=== Financial Summary: {data.company_name} ({data.ticker}) ===

Company: {data.company_name}
Sector: {data.sector} | Industry: {data.industry}
Currency: {data.currency}

── Price & Valuation ──
Current Price:     {data.currency} {data.current_price or 'N/A'}
Market Cap:        {format_large_number(data.market_cap)}
P/E Ratio:         {data.pe_ratio or 'N/A'}
...
""".strip()
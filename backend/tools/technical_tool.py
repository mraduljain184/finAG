"""
finAG — Technical Analysis Tool
Computes technical indicators from historical price data.
Uses the `ta` (technical analysis) library + pandas.
"""

import pandas as pd
import ta
from loguru import logger
from models.schemas import TechnicalAnalysis, TrendDirection
from tools.yfinance_tool import fetch_price_history

def compute_technical_analysis(ticker: str) -> TechnicalAnalysis:
    """
    Compute full technical analysis for a ticker.
    """
    logger.info(f"Computing technical analysis for {ticker}")

    # Fetch price data
    history = fetch_price_history(ticker, period="1y")
    df = pd.DataFrame({
        "date": pd.to_datetime(history["dates"]),
        "close": history["close"],
        "high": history["high"],
        "low": history["low"],
        "volume": history["volume"],
    })
    df.set_index("date", inplace=True)

    if len(df) < 50:
        raise ValueError(f"Insufficient price data for {ticker} (need 50+ days, got {len(df)})")

    close = df["close"]
    current_price = close.iloc[-1]

    # Moving Averages
    sma_50 = close.rolling(window=50).mean().iloc[-1]
    sma_200 = close.rolling(window=200).mean().iloc[-1] if len(close) >= 200 else None
    ema_20 = close.ewm(span=20, adjust=False).mean().iloc[-1]

    # RSI (14-period)
    rsi_series = ta.momentum.RSIIndicator(close, window=14).rsi()
    rsi_14 = rsi_series.iloc[-1] if not rsi_series.empty else None

    # MACD (12, 26, 9)
    macd_indicator = ta.trend.MACD(close, window_slow=26, window_fast=12, window_sign=9)
    macd_val = macd_indicator.macd().iloc[-1]
    macd_signal = macd_indicator.macd_signal().iloc[-1]
    macd_hist = macd_indicator.macd_diff().iloc[-1]

    # Support & Resistance
    recent = df.tail(20)
    support = recent["low"].min()
    resistance = recent["high"].max()

    # Trend Detection
    trend = TrendDirection.SIDEWAYS
    if sma_200 is not None:
        if current_price > sma_50 > sma_200:
            trend = TrendDirection.UPTREND
        elif current_price < sma_50 < sma_200:
            trend = TrendDirection.DOWNTREND

    golden_cross = False
    death_cross = False
    if sma_200 is not None and len(close) >= 201:
        sma50_series = close.rolling(50).mean()
        sma200_series = close.rolling(200).mean()
        for i in range(-5, 0):
            if (
                sma50_series.iloc[i - 1] < sma200_series.iloc[i - 1]
                and sma50_series.iloc[i] > sma200_series.iloc[i]
            ):
                golden_cross = True
            if (
                sma50_series.iloc[i - 1] > sma200_series.iloc[i - 1]
                and sma50_series.iloc[i] < sma200_series.iloc[i]
            ):
                death_cross = True

    summary_parts = []

    if current_price > sma_50:
        summary_parts.append(f"Price (${current_price:.2f}) is ABOVE the 50-day SMA (${sma_50:.2f}), bullish signal.")
    else:
        summary_parts.append(f"Price (${current_price:.2f}) is BELOW the 50-day SMA (${sma_50:.2f}), bearish signal.")
    
    if rsi_14 is not None:
        if rsi_14 > 70:
            summary_parts.append(f"RSI at {rsi_14:.1f} — OVERBOUGHT territory (>70). Potential pullback ahead.")
        elif rsi_14 < 30:
            summary_parts.append(f"RSI at {rsi_14:.1f} — OVERSOLD territory (<30). Potential bounce opportunity.")
        else:
            summary_parts.append(f"RSI at {rsi_14:.1f} — neutral range.")

    result = TechnicalAnalysis(
        ticker=ticker.upper(),
        current_price=round(current_price, 2),
        sma_50=round(sma_50, 2),
        sma_200=round(sma_200, 2) if sma_200 is not None else None,
        ema_20=round(ema_20, 2),
        rsi_14=round(rsi_14, 2) if rsi_14 is not None else None,
        macd=round(macd_val, 4) if macd_val is not None else None,
        macd_signal=round(macd_signal, 4) if macd_signal is not None else None,
        macd_histogram=round(macd_hist, 4) if macd_hist is not None else None,
        support_level=round(support, 2),
        resistance_level=round(resistance, 2),
        trend=trend,
        golden_cross=golden_cross,
        death_cross=death_cross,
        analysis_summary="\n".join(summary_parts),
    )

    logger.success(f"Technical analysis complete for {ticker}: trend={trend.value}")
    return result
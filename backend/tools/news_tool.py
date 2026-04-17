"""
finAG — News Tool
Fetches recent news articles about a company.
Supports: Google News RSS (free, no key), NewsAPI (with key).
"""

import feedparser
import requests
from datetime import datetime, timedelta
from loguru import logger
from config import settings
from urllib.parse import quote_plus


def fetch_news_google(query: str, max_results: int = 10) -> list[dict]:
    """
    Fetch news from Google News RSS feed (free, no API key needed).
    """
    logger.info(f"Fetching Google News for: {query}")

    # Google News RSS URL
    encoded_query = quote_plus(f"{query} stock")
    url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en&gl=US&ceid=US:en"

    try:
            feed = feedparser.parse(url)
    except Exception as e:
        logger.warning(f"Google News RSS failed: {e}")
        return []
    
    articles = []
    for entry in feed.entries[:max_results]:
        # Extract source from title (Google News format: "Title - Source")
        title = entry.get("title", "")
        source = ""
        if " - " in title:
            parts = title.rsplit(" - ", 1)
            title = parts[0]
            source = parts[1] if len(parts) > 1 else ""

        articles.append({
            "title": title,
            "source": source,
            "url": entry.get("link", ""),
            "published_at": entry.get("published", ""),
            "summary": entry.get("summary", "")[:500],
        })

    logger.info(f"Found {len(articles)} articles from Google News")
    return articles

def fetch_news_newsapi(query: str, max_results: int = 10) -> list[dict]:
    """
    Fetch news from NewsAPI.org (requires API key).
    """
    if not settings.NEWS_API_KEY:
        logger.warning("No NEWS_API_KEY configured, skipping NewsAPI")
        return []

    logger.info(f"Fetching NewsAPI results for: {query}")

    from_date = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")

    try:
        resp = requests.get(
            "https://newsapi.org/v2/everything",
            params={
                "q": query,
                "from": from_date,
                "sortBy": "relevancy",
                "pageSize": max_results,
                "language": "en",
                "apiKey": settings.NEWS_API_KEY,
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.warning(f"NewsAPI request failed: {e}")
        return []
    
    articles = []
    for article in data.get("articles", []):
        articles.append({
            "title": article.get("title", ""),
            "source": article.get("source", {}).get("name", ""),
            "url": article.get("url", ""),
            "published_at": article.get("publishedAt", ""),
            "summary": (article.get("description") or "")[:500],
        })

    logger.info(f"Found {len(articles)} articles from NewsAPI")
    return articles


def fetch_news(company_name: str, ticker: str, max_results: int = 10) -> list[dict]:
    """
    Fetch news using the best available source.
    Tries NewsAPI first (if key configured), falls back to Google News RSS.
    """
    # Build a good search query
    query = f"{company_name} {ticker}"

    # Try NewsAPI first
    articles = fetch_news_newsapi(query, max_results)

    # Fall back to Google News
    if not articles:
        articles = fetch_news_google(query, max_results)

    # Deduplicate by title similarity
    seen_titles = set()
    unique = []
    for article in articles:
        title_lower = article["title"].lower().strip()
        if title_lower not in seen_titles and article["title"]:
            seen_titles.add(title_lower)
            unique.append(article)

    return unique[:max_results]
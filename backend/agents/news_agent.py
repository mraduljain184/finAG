"""
finAG — News Sentiment Agent
Fetches recent news and uses Claude to analyze sentiment.
Acts as a media analyst who reads between the headlines.
"""

import json
from loguru import logger
from tools.news_tool import fetch_news
from tools.yfinance_tool import fetch_financial_data
from tools.llm_tool import ask_llm, ask_llm_json
from models.schemas import NewsSentiment, NewsArticle, SentimentLabel

NEWS_AGENT_SYSTEM_PROMPT = """You are a financial media analyst specializing in sentiment analysis.
Your job is to read news headlines and summaries about a company, then assess the overall market sentiment.

For each article, determine:
- Sentiment: "Positive", "Negative", or "Neutral"
- Score: A number from -1.0 (very negative) to 1.0 (very positive). 0.0 is neutral.

Then provide an overall assessment:
- What is the dominant narrative in the news?
- Are there any concerning patterns (multiple negative articles, lawsuits, regulatory issues)?
- Are there positive catalysts (new products, partnerships, strong earnings)?

Rules:
- Base sentiment ONLY on the article content, not your prior knowledge.
- A headline about "stock price falling" is Negative. A headline about "record revenue" is Positive.
- If the article is about the industry generally and not specific to the company, mark it Neutral.
- Be precise. Don't say "mostly positive" — say "7 out of 10 articles were positive, focused on product launches and revenue growth."
"""

SENTIMENT_JSON_PROMPT = """Analyze each article and return a JSON object with this exact structure:
{
    "articles": [
        {
            "title": "article title here",
            "sentiment": "Positive" or "Negative" or "Neutral",
            "score": 0.0 to 1.0 or -1.0 to 0.0,
            "summary": "one sentence summary of why this sentiment"
        }
    ],
    "overall_sentiment": "Positive" or "Negative" or "Neutral",
    "overall_score": -1.0 to 1.0,
    "analysis_summary": "2-3 sentence overall narrative"
}
"""

def run_news_agent(ticker: str) -> NewsSentiment:
    """
    Run the news sentiment agent.

    1. Fetches company name from yfinance
    2. Fetches recent news articles
    3. Sends articles to Claude for sentiment analysis
    4. Returns structured sentiment data

    Args:
        ticker: Stock ticker symbol

    Returns:
        NewsSentiment object with scored articles and overall sentiment
    """
    logger.info(f"[News Agent] Starting sentiment analysis for {ticker}")

    # Step 1: Get company name for better news search
    financial_data = fetch_financial_data(ticker)
    company_name = financial_data.company_name

    # Step 2: Fetch news articles
    articles = fetch_news(company_name, ticker, max_results=10)

    if not articles:
        logger.warning(f"[News Agent] No articles found for {ticker}")
        return NewsSentiment(
            ticker=ticker.upper(),
            overall_sentiment=SentimentLabel.NEUTRAL,
            analysis_summary="No recent news articles found for analysis.",
        )
    
    # Step 3: Format articles for Claude
    articles_text = ""
    for i, article in enumerate(articles, 1):
        articles_text += f"""
Article {i}:
Title: {article['title']}
Source: {article['source']}
Date: {article['published_at']}
Summary: {article['summary'] or 'No summary available'}
---
"""
        # Step 4: Ask Claude to analyze sentiment
    prompt = f"""Analyze the sentiment of the following {len(articles)} news articles about {company_name} ({ticker}).

{articles_text}

{SENTIMENT_JSON_PROMPT}
"""

    try:
        response = ask_llm_json(prompt, system_prompt=NEWS_AGENT_SYSTEM_PROMPT, max_tokens=2000)

        # Parse Claude's JSON response
        # Clean up common JSON formatting issues
        response = response.strip()
        if response.startswith("```"):
            response = response.split("\n", 1)[1]
        if response.endswith("```"):
            response = response.rsplit("```", 1)[0]

        sentiment_data = json.loads(response)
    
    except (json.JSONDecodeError, Exception) as e:
        logger.warning(f"[News Agent] Failed to parse LLM JSON response: {e}")
        logger.info("[News Agent] Falling back to simple analysis...")

        # Fallback: ask for plain text analysis instead
        fallback_prompt = f"""Analyze the overall sentiment of these news articles about {company_name} ({ticker}).
Are they mostly positive, negative, or neutral? Give a brief 2-3 sentence summary.

{articles_text}"""

        analysis = ask_llm(fallback_prompt, system_prompt=NEWS_AGENT_SYSTEM_PROMPT, max_tokens=500)

        return NewsSentiment(
            ticker=ticker.upper(),
            overall_sentiment=SentimentLabel.NEUTRAL,
            analysis_summary=analysis,
            articles=[
                NewsArticle(title=a["title"], source=a["source"], url=a["url"], published_at=a["published_at"])
                for a in articles
            ],
        )
    
    # Step 5: Build the structured response
    scored_articles = []
    for article_data in sentiment_data.get("articles", []):
        # Match back to original article URLs
        original = next(
            (a for a in articles if a["title"] in article_data.get("title", "")),
            {}
        )

        sentiment_str = article_data.get("sentiment", "Neutral")
        try:
            sentiment = SentimentLabel(sentiment_str)
        except ValueError:
            sentiment = SentimentLabel.NEUTRAL

        scored_articles.append(NewsArticle(
            title=article_data.get("title", ""),
            source=original.get("source", ""),
            url=original.get("url", ""),
            published_at=original.get("published_at", ""),
            summary=article_data.get("summary", ""),
            sentiment=sentiment,
            sentiment_score=float(article_data.get("score", 0.0)),
        ))

    # Calculate counts
    positive_count = sum(1 for a in scored_articles if a.sentiment == SentimentLabel.POSITIVE)
    negative_count = sum(1 for a in scored_articles if a.sentiment == SentimentLabel.NEGATIVE)
    neutral_count = sum(1 for a in scored_articles if a.sentiment == SentimentLabel.NEUTRAL)

    # Determine overall sentiment
    overall_str = sentiment_data.get("overall_sentiment", "Neutral")
    try:
        overall_sentiment = SentimentLabel(overall_str)
    except ValueError:
        overall_sentiment = SentimentLabel.NEUTRAL

    result = NewsSentiment(
        ticker=ticker.upper(),
        overall_sentiment=overall_sentiment,
        overall_score=float(sentiment_data.get("overall_score", 0.0)),
        positive_count=positive_count,
        negative_count=negative_count,
        neutral_count=neutral_count,
        articles=scored_articles,
        analysis_summary=sentiment_data.get("analysis_summary", ""),
    )

    logger.success(
        f"[News Agent] Sentiment for {ticker}: {overall_sentiment.value} "
        f"(+{positive_count} / -{negative_count} / ~{neutral_count})"
    )

    return result
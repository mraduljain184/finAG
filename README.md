# finAG — AI Equity Research Agent

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://react.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A multi-agent AI system that generates professional equity research reports. Enter a ticker, get a Buy/Hold/Sell recommendation with target price, technical analysis, news sentiment, competitor benchmarking, and a downloadable PDF — in about 30 seconds.

## How It Works

Five specialized LLM agents collaborate in a sequential pipeline, each with its own system prompt, data sources, and Pydantic-validated output schema:

```
     ┌──────────────┐
     │  User: AAPL  │
     └──────┬───────┘
            │
     ┌──────▼───────────────────────────────────────┐
     │         Orchestrator (ResearchCrew)          │
     └──────┬───────────────────────────────────────┘
            │
    ┌───────┼───────┬───────────┬──────────────┐
    │       │       │           │              │
    ▼       ▼       ▼           ▼              ▼
┌─────────┐ ┌──────┐ ┌─────────┐ ┌───────────┐ ┌──────────┐
│Financial│ │ News │ │Technical│ │Competitor │ │  Report  │
│  Agent  │ │Agent │ │  Agent  │ │   Agent   │ │  Writer  │
└─────────┘ └──────┘ └─────────┘ └───────────┘ └────┬─────┘
                                                    │
                                           ┌────────▼────────┐
                                           │  Final Report   │
                                           │  + PDF Export   │
                                           └─────────────────┘
```

| Agent | Role | Data Sources |
|-------|------|-------------|
| Financial | Fundamental analysis — valuation, profitability, financial health | yfinance |
| News | Sentiment scoring across recent articles | Google News RSS, NewsAPI |
| Technical | RSI, MACD, SMA/EMA crossovers, support/resistance | yfinance + custom indicators |
| Competitor | Peer comparison, moat assessment | yfinance (autonomous peer discovery) |
| Report Writer | Synthesizes all specialist outputs into final Buy/Hold/Sell | — |

## Tech Stack

**Backend:** Python 3.11 · FastAPI · Pydantic · WeasyPrint · Jinja2 · loguru · slowapi · cachetools
**LLM:** Groq (Llama 3.3 70B) — pluggable architecture supporting Anthropic, OpenAI, Gemini, Groq
**Data:** yfinance · Google News RSS · NewsAPI
**Frontend:** React 18 · Vite · TailwindCSS · Recharts · axios · lucide-react
**Infra:** Docker · Railway (backend) · Vercel (frontend)

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Groq API key (free tier at [console.groq.com](https://console.groq.com))

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp ../.env.example ../.env
# Edit .env and add your GROQ_API_KEY

uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:5173`, enter a ticker (try `AAPL`, `MSFT`, `TSLA`, or `RELIANCE.NS` for Indian stocks), and get your report.

### Docker

```bash
docker build -t finag-backend .
docker run --rm -p 8000:8000 --env-file .env finag-backend
```

## API Endpoints

| Method | Path | Description | Rate Limit |
|--------|------|-------------|------------|
| GET | `/health` | Health check | — |
| POST | `/analyze` | Full research report (JSON) | 10/hour |
| POST | `/analyze/pdf` | Research report as PDF download | 10/hour |
| GET | `/admin/cache/stats` | Cache hit rate, size, entries | — |
| POST | `/admin/cache/clear` | Flush the cache | — |

### Example Request

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"ticker": "NVDA"}'
```

### Example Response (truncated)

```json
{
  "ticker": "NVDA",
  "company_name": "NVIDIA Corporation",
  "total_time_seconds": 16.2,
  "report": {
    "recommendation": "Buy",
    "target_price": 250.0,
    "confidence": 70.0,
    "executive_summary": "...",
    "key_strengths": ["Strong market presence", "..."],
    "key_risks": ["Potential overvaluation", "..."]
  },
  "financial": { "...": "..." },
  "news_sentiment": { "...": "..." },
  "technical": { "...": "..." },
  "competitor": { "...": "..." }
}
```

## Performance

- **Cold call:** ~15–20s (5 LLM calls + yfinance fetches)
- **Cached call:** <100ms (24h TTL, 100-entry in-memory cache)
- **PDF generation:** +2s on top of analysis

## Project Structure

```
finAG/
├── backend/
│   ├── agents/          # 5 specialist agents
│   ├── tools/           # yfinance, news, technical, LLM, PDF, cache
│   ├── crew/            # orchestration layer
│   ├── models/          # Pydantic schemas
│   ├── templates/       # Jinja2 HTML for PDF
│   └── main.py          # FastAPI app
├── frontend/
│   └── src/
│       ├── api/         # axios client
│       ├── components/  # ReportView, AgentProgress, PriceChart
│       └── App.jsx
├── Dockerfile
└── .env.example
```

## Roadmap

- [ ] Redis-backed cache (currently in-memory)
- [ ] Streaming agent progress via Server-Sent Events
- [ ] Historical report storage (Postgres)
- [ ] Portfolio-level analysis (multi-ticker)
- [ ] Fine-tuned sentiment model for financial news

## Disclaimer

This project is for educational and research purposes only. Output should not be considered financial advice. Always consult a licensed financial advisor before making investment decisions.

## License

MIT

## Author

**Mradul Jain** · [@mraduljain184](https://github.com/mraduljain184) · RGIPT
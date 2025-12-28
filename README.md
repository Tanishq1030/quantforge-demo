# QuantForge: Multi-Agent AI for Financial Markets

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

> **Production-grade AI system combining LLM agents, vector memory, and time-series analysis for financial markets**

Built for **GSoC 2026** (Apache Beam ML pipeline integration planned)

---

##  What Makes QuantForge Unique

**First-of-its-kind** open-source multi-agent system specifically designed for financial analysis:

- ** Multi-Agent Orchestration**: Specialized AI agents (market analyst, sentiment analyzer, risk manager) collaborate via LangChain
- ** Vector Memory**: Semantic search & reasoning using Weaviate embeddings
- ** Smart Data Pipeline**: 7+ free data sources with automatic fallback (yfinance, Finnhub, FMP, Polygon, Alpha Vantage, Twelve Data, IEX Cloud)
- ** Real-time Streaming**: WebSocket-ready for live market data
- ** Fault Tolerance**: Built-in retry logic, rate limiting, and graceful degradation

---

##  Architecture

```
┌─────────────────────────────────────────────────────┐
│                  LLM Agents Layer                    │
│  (Market Analyst • Sentiment • Risk • Portfolio)    │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────┐
│              Orchestration Engine                    │
│         (LangChain + Custom Workflows)              │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────┐
│              Vector Memory Store                     │
│         (Weaviate + Embeddings Search)              │
└─────────────────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────┐
│           Data Ingestion Pipeline                    │
│  (7 Free Sources + Auto-Fallback + Rate Limiting)  │
└─────────────────────────────────────────────────────┘
```

---

##  Quick Demo

### Fetch Stock Data with Auto-Fallback

```python
from connectors import fetch_with_fallback

# Automatically tries all available sources until success
data = fetch_with_fallback("AAPL", interval="1d", lookback_days=30)

for bar in data[:5]:
    print(f"{bar.timestamp}: ${bar.close:.2f}")
```

**Output:**
```
2024-01-15: $193.50
2024-01-16: $194.25
2024-01-17: $192.80
...
```

### Use Specific Connectors

```python
from connectors import yfinance_connector, finnhub_connector

# Direct connector usage
yf_data = yfinance_connector.fetch_ohlcv("TSLA", interval="1h")
fh_data = finnhub_connector.fetch_ohlcv("MSFT", interval="1d")
```

---

##  Installation

```bash
# Clone the demo
git clone https://github.com/YOUR_USERNAME/quantforge-demo.git
cd quantforge-demo

# Install dependencies
pip install -r requirements.txt

# Run demo
python demo.py
```

---

##  Tech Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python 3.11+, FastAPI, Pydantic |
| **ML/AI** | PyTorch, LangChain, OpenAI/Anthropic APIs |
| **Data** | pandas, yfinance, multiple financial APIs |
| **Vector DB** | Weaviate (semantic search) |
| **Cache** | Redis |
| **Database** | PostgreSQL + Alembic migrations |
| **Async** | asyncio, Celery task queue |
| **Monitoring** | Loguru, Prometheus metrics |

---

##  Key Features

### 1. **Smart Data Connectors**
-  7 free data sources (no Intrinio subscription needed!)
-  Automatic fallback if primary source fails
-  Built-in rate limiting (respects API quotas)
-  Retry logic with exponential backoff

### 2. **Multi-Agent System** *(Full implementation in private repo)*
- Market Analyst Agent (technical analysis)
- Sentiment Agent (news/social media analysis)
- Risk Manager Agent (portfolio risk assessment)
- Portfolio Manager Agent (allocation recommendations)

### 3. **Vector Memory**
- Store financial reports, news, earnings calls
- Semantic search for contextual reasoning
- LLM can reference past market events

### 4. **Production-Ready**
- Docker Compose setup
- Health check endpoints
- Structured logging
- Error tracking

---

##  Data Sources Comparison

| Source | Free Tier | Rate Limit | API Key |
|--------|-----------|------------|---------|
| **yfinance** | Unlimited | None |  No |
| **Finnhub** | 60 calls/min | 60/min |  Yes |
| **FMP** | 250/day | 5/min |  Yes |
| **Alpha Vantage** | 25/day | 5/min |  Yes |
| **Polygon** | 5/min | 5/min |  Yes |
| **Twelve Data** | 800/day | 8/min |  Yes |
| **IEX Cloud** | 50k/month | 100/min |  Yes |

*QuantForge automatically tries each source in order until data is retrieved*

---

##  GSoC 2026 Vision

### Planned Apache Beam Integration

**Why Beam?**
- Scale data pipelines for multi-asset analysis (1000s of stocks)
- Real-time streaming with `DoFn` transforms
- ML inference via `RunInference` for PyTorch models
- Cross-platform (local dev → production GCP)

**Proposed Contributions:**
1. **Beam Python SDK**: Add financial time-series I/O connectors
2. **RunInference**: Extend for LLM chain orchestration
3. **Examples**: Multi-agent workflow demo using Beam pipelines

---

##  Contributing

This demo showcases the **data ingestion layer**. The full QuantForge system (agents, memory, orchestration) is in active development.

**Interested in collaborating?**
-  Open an issue for feature requests
-  Report bugs or connector issues
-  Star the repo if you find it useful!

---

MIT License - see LICENSE file

---

## Acknowledgments

Built as a demonstration of production-grade AI architecture for financial markets. This project showcases multi-source data integration, fault-tolerant design, and scalable pipeline patterns suitable for Apache Beam integration.

**Feedback and contributions welcome!**


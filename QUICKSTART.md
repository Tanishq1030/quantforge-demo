# QuantForge Demo - Quick Start

## Setup (5 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run demo
python demo.py
```

## What You'll See

- ✅ Available data connectors
- 📊 AAPL stock data (7 days)
- 📊 TSLA stock data (5 days)
- 🔄 Automatic fallback demonstration

## Add API Keys (Optional)

For more data sources, create `.env`:

```bash
# Alpha Vantage (25 free calls/day)
ALPHA_VANTAGE_API_KEY=your_key_here

# Finnhub (60 calls/min)
FINNHUB_API_KEY=your_key_here

# FMP (250 calls/day)
FMP_API_KEY=your_key_here

# Polygon (5 calls/min)
POLYGON_API_KEY=your_key_here

# Twelve Data (800 calls/day)
TWELVE_DATA_API_KEY=your_key_here

# IEX Cloud (50k calls/month)
IEX_CLOUD_API_KEY=your_key_here
```

**Note:** yfinance works without any API key!

## Project Structure

```
quantforge-demo/
├── README.md           # Main documentation
├── QUICKSTART.md       # This file
├── demo.py             # Demo script
├── connectors.py       # 7 data connectors
├── requirements.txt    # Dependencies
├── .gitignore
└── LICENSE
```

## Next Steps

1. ⭐ Star the repo
2. 🔧 Try different tickers/intervals
3. 📝 Read main README.md for architecture details
4. 🤝 Open issues for questions

**Built for GSoC 2026!** 🚀

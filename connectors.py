"""
QuantForge AI Engine - Equity Data Connectors

Consolidated connectors for stock/equity market data.

FREE SOURCES (No Payment Required):
- yfinance:      FREE, unlimited (no API key)
- alpha_vantage: FREE 25/day (requires key)
- finnhub:       FREE 60/min (requires key)
- twelve_data:   FREE 800/day (requires key)
- fmp:           FREE 250/day (requires key)
- polygon:       FREE 5/min (requires key)
- iex_cloud:     FREE 50k/month (requires key)

Usage:
    from backend.engine.ingestion.equity_connectors import yfinance_connector
    
    data = yfinance_connector.fetch_ohlcv("AAPL", interval="1d", lookback_days=30)
"""
import time
import os
import requests
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional
from loguru import logger


# =============================================================================
# DATA MODELS
# =============================================================================

@dataclass
class OHLCVData:
    """OHLCV (Open, High, Low, Close, Volume) data point"""
    timestamp: datetime
    ticker: str
    interval: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: Optional[float] = None
    source: str = "unknown"


# =============================================================================
# BASE CONNECTOR
# =============================================================================

class RateLimiter:
    """Simple rate limiter to respect API limits"""
    
    def __init__(self, requests_per_window: int = 5, window_seconds: int = 60):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self._request_times: dict[str, list[float]] = {}
    
    def wait_if_needed(self, key: str = "default"):
        """Wait if rate limit exceeded"""
        now = time.time()
        if key not in self._request_times:
            self._request_times[key] = []
        
        # Clean old timestamps
        cutoff = now - self.window_seconds
        self._request_times[key] = [t for t in self._request_times[key] if t > cutoff]
        
        # Wait if at limit
        if len(self._request_times[key]) >= self.requests_per_window:
            sleep_time = self._request_times[key][0] - cutoff + 0.1
            if sleep_time > 0:
                logger.debug(f"Rate limit: sleeping {sleep_time:.1f}s")
                time.sleep(sleep_time)
        
        self._request_times[key].append(now)


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Decorator for exponential backoff retry"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    delay = base_delay * (2 ** attempt)
                    logger.warning(f"Retry {attempt + 1}/{max_retries} after {delay}s: {e}")
                    time.sleep(delay)
            return []
        return wrapper
    return decorator


class DataConnector(ABC):
    """Base class for all data connectors"""
    
    SOURCE_NAME: str = "base"
    SUPPORTED_INTERVALS: list[str] = []
    RATE_LIMIT_REQUESTS: int = 5
    RATE_LIMIT_WINDOW: int = 60
    
    def __init__(self):
        self.rate_limiter = RateLimiter(
            self.RATE_LIMIT_REQUESTS,
            self.RATE_LIMIT_WINDOW
        )
    
    @abstractmethod
    def fetch_ohlcv(self, ticker: str, interval: str = "1d", lookback_days: int = 30) -> list[OHLCVData]:
        """Fetch OHLCV data for a ticker"""
        pass
    
    def is_available(self) -> bool:
        """Check if connector is available"""
        return True


# =============================================================================
# YFINANCE - FREE, No API Key Required (BEST DEFAULT)
# =============================================================================

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    yf = None


class YFinanceConnector(DataConnector):
    """
    Yahoo Finance - FREE, unlimited, no API key required.
    
    Best default source for historical data.
    """
    
    SOURCE_NAME = "yfinance"
    SUPPORTED_INTERVALS = ["1m", "5m", "15m", "30m", "1h", "1d", "1w"]
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 60
    
    def __init__(self):
        super().__init__()
        if not YFINANCE_AVAILABLE:
            raise ImportError("yfinance not installed. Run: pip install yfinance")
    
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def fetch_ohlcv(self, ticker: str, interval: str = "1d", lookback_days: int = 30) -> list[OHLCVData]:
        """Fetch OHLCV data from Yahoo Finance"""
        self.rate_limiter.wait_if_needed(ticker)
        
        # Map interval
        interval_map = {"1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m", 
                        "1h": "1h", "1d": "1d", "1w": "1wk"}
        yf_interval = interval_map.get(interval, "1d")
        
        logger.info(f"Fetching {ticker} from yfinance ({interval})")
        stock = yf.Ticker(ticker)
        df = stock.history(period=f"{lookback_days}d", interval=yf_interval)
        
        result = []
        for idx, row in df.iterrows():
            result.append(OHLCVData(
                timestamp=idx.to_pydatetime(),
                ticker=ticker.upper(),
                interval=interval,
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                volume=int(row["Volume"]),
                adj_close=float(row.get("Adj Close", row["Close"])),
                source=self.SOURCE_NAME
            ))
        return result


# =============================================================================
# ALPHA VANTAGE - FREE 25/day
# =============================================================================

ALPHA_VANTAGE_AVAILABLE = bool(os.getenv("ALPHA_VANTAGE_API_KEY", ""))


class AlphaVantageConnector(DataConnector):
    """Alpha Vantage - adjusted data, FREE 25/day."""
    
    SOURCE_NAME = "alpha_vantage"
    BASE_URL = "https://www.alphavantage.co/query"
    SUPPORTED_INTERVALS = ["1m", "5m", "15m", "30m", "1h", "1d", "1w"]
    RATE_LIMIT_REQUESTS = 5
    RATE_LIMIT_WINDOW = 60
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY", "")
    
    @retry_with_backoff(max_retries=3, base_delay=2.0)
    def fetch_ohlcv(self, ticker: str, interval: str = "1d", lookback_days: int = 30) -> list[OHLCVData]:
        if not self.api_key:
            return []
        self.rate_limiter.wait_if_needed(ticker)
        
        # Daily data
        if interval in ["1d", "1w"]:
            function = "TIME_SERIES_DAILY_ADJUSTED"
            data_key = "Time Series (Daily)"
        else:
            function = "TIME_SERIES_INTRADAY"
            data_key = f"Time Series ({interval})"
        
        logger.info(f"Fetching {ticker} from Alpha Vantage")
        resp = requests.get(self.BASE_URL, params={
            "function": function,
            "symbol": ticker,
            "apikey": self.api_key,
            "outputsize": "compact" if lookback_days <= 100 else "full",
            "interval": interval if interval not in ["1d", "1w"] else None
        }, timeout=30)
        
        if resp.status_code != 200:
            return []
        
        data = resp.json()
        time_series = data.get(data_key, {})
        
        result = []
        cutoff = datetime.now() - timedelta(days=lookback_days)
        
        for date_str, values in time_series.items():
            try:
                ts = datetime.strptime(date_str.split()[0], "%Y-%m-%d")
                if ts < cutoff:
                    continue
                result.append(OHLCVData(
                    timestamp=ts, ticker=ticker.upper(), interval=interval,
                    open=float(values.get("1. open", 0)),
                    high=float(values.get("2. high", 0)),
                    low=float(values.get("3. low", 0)),
                    close=float(values.get("4. close", 0)),
                    volume=int(values.get("6. volume", values.get("5. volume", 0))),
                    adj_close=float(values.get("5. adjusted close", values.get("4. close", 0))),
                    source=self.SOURCE_NAME
                ))
            except (KeyError, ValueError):
                continue
        
        result.sort(key=lambda x: x.timestamp)
        return result


# =============================================================================
# FINNHUB - FREE 60/min
# =============================================================================

FINNHUB_AVAILABLE = bool(os.getenv("FINNHUB_API_KEY", ""))


class FinnhubConnector(DataConnector):
    """Finnhub - stocks + company news, FREE 60/min."""
    
    SOURCE_NAME = "finnhub"
    BASE_URL = "https://finnhub.io/api/v1"
    SUPPORTED_INTERVALS = ["1m", "5m", "15m", "30m", "1h", "1d", "1w"]
    RATE_LIMIT_REQUESTS = 60
    RATE_LIMIT_WINDOW = 60
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv("FINNHUB_API_KEY", "")
    
    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def fetch_ohlcv(self, ticker: str, interval: str = "1d", lookback_days: int = 30) -> list[OHLCVData]:
        if not self.api_key:
            return []
        self.rate_limiter.wait_if_needed(ticker)
        
        # Map interval to resolution
        res_map = {"1m": "1", "5m": "5", "15m": "15", "30m": "30", 
                   "1h": "60", "1d": "D", "1w": "W"}
        resolution = res_map.get(interval, "D")
        
        end = int(datetime.now().timestamp())
        start = int((datetime.now() - timedelta(days=lookback_days)).timestamp())
        
        logger.info(f"Fetching {ticker} from Finnhub")
        resp = requests.get(f"{self.BASE_URL}/stock/candle", params={
            "symbol": ticker.upper(),
            "resolution": resolution,
            "from": start,
            "to": end,
            "token": self.api_key
        }, timeout=30)
        
        if resp.status_code != 200:
            return []
        
        data = resp.json()
        if data.get("s") != "ok":
            return []
        
        result = []
        timestamps = data.get("t", [])
        opens = data.get("o", [])
        highs = data.get("h", [])
        lows = data.get("l", [])
        closes = data.get("c", [])
        volumes = data.get("v", [])
        
        for i in range(len(timestamps)):
            result.append(OHLCVData(
                timestamp=datetime.fromtimestamp(timestamps[i]),
                ticker=ticker.upper(), interval=interval,
                open=float(opens[i]), high=float(highs[i]),
                low=float(lows[i]), close=float(closes[i]),
                volume=int(volumes[i]), source=self.SOURCE_NAME
            ))
        return result
    
    def fetch_news(self, ticker: str, lookback_days: int = 7) -> list[dict]:
        """Fetch company news"""
        if not self.api_key:
            return []
        self.rate_limiter.wait_if_needed(ticker)
        
        end = datetime.now().strftime("%Y-%m-%d")
        start = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
        
        resp = requests.get(f"{self.BASE_URL}/company-news", params={
            "symbol": ticker.upper(),
            "from": start, "to": end,
            "token": self.api_key
        }, timeout=30)
        
        return resp.json() if resp.status_code == 200 else []


# =============================================================================
# TWELVE DATA - FREE 800/day
# =============================================================================

TWELVE_DATA_AVAILABLE = bool(os.getenv("TWELVE_DATA_API_KEY", ""))


class TwelveDataConnector(DataConnector):
    """Twelve Data - multi-asset, FREE 800/day."""
    
    SOURCE_NAME = "twelve_data"
    BASE_URL = "https://api.twelvedata.com"
    SUPPORTED_INTERVALS = ["1m", "5m", "15m", "30m", "1h", "1d", "1w"]
    RATE_LIMIT_REQUESTS = 8
    RATE_LIMIT_WINDOW = 60
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv("TWELVE_DATA_API_KEY", "")
    
    @retry_with_backoff(max_retries=3, base_delay=2.0)
    def fetch_ohlcv(self, ticker: str, interval: str = "1d", lookback_days: int = 30) -> list[OHLCVData]:
        if not self.api_key:
            return []
        self.rate_limiter.wait_if_needed(ticker)
        
        interval_map = {"1m": "1min", "5m": "5min", "15m": "15min", 
                        "30m": "30min", "1h": "1h", "1d": "1day", "1w": "1week"}
        td_interval = interval_map.get(interval, "1day")
        
        logger.info(f"Fetching {ticker} from Twelve Data")
        resp = requests.get(f"{self.BASE_URL}/time_series", params={
            "symbol": ticker.upper(),
            "interval": td_interval,
            "outputsize": min(lookback_days * 7, 5000),
            "apikey": self.api_key
        }, timeout=30)
        
        if resp.status_code != 200:
            return []
        
        data = resp.json()
        if "values" not in data:
            return []
        
        result = []
        cutoff = datetime.now() - timedelta(days=lookback_days)
        
        for item in data["values"]:
            try:
                ts = datetime.strptime(item["datetime"], "%Y-%m-%d %H:%M:%S" 
                                        if " " in item["datetime"] else "%Y-%m-%d")
                if ts < cutoff:
                    continue
                result.append(OHLCVData(
                    timestamp=ts, ticker=ticker.upper(), interval=interval,
                    open=float(item["open"]), high=float(item["high"]),
                    low=float(item["low"]), close=float(item["close"]),
                    volume=int(item.get("volume", 0)), source=self.SOURCE_NAME
                ))
            except (KeyError, ValueError):
                continue
        
        result.sort(key=lambda x: x.timestamp)
        return result


# =============================================================================
# FMP (Financial Modeling Prep) - FREE 250/day
# =============================================================================

FMP_AVAILABLE = bool(os.getenv("FMP_API_KEY", ""))


class FMPConnector(DataConnector):
    """Financial Modeling Prep - fundamentals + prices, FREE 250/day."""
    
    SOURCE_NAME = "fmp"
    BASE_URL = "https://financialmodelingprep.com/api/v3"
    SUPPORTED_INTERVALS = ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
    RATE_LIMIT_REQUESTS = 5
    RATE_LIMIT_WINDOW = 60
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv("FMP_API_KEY", "")
    
    @retry_with_backoff(max_retries=3, base_delay=2.0)
    def fetch_ohlcv(self, ticker: str, interval: str = "1d", lookback_days: int = 30) -> list[OHLCVData]:
        if not self.api_key:
            return []
        self.rate_limiter.wait_if_needed(ticker)
        
        if interval == "1d":
            url = f"{self.BASE_URL}/historical-price-full/{ticker.upper()}"
        else:
            url = f"{self.BASE_URL}/historical-chart/{interval}/{ticker.upper()}"
        
        logger.info(f"Fetching {ticker} from FMP")
        resp = requests.get(url, params={"apikey": self.api_key}, timeout=30)
        
        if resp.status_code != 200:
            return []
        
        data = resp.json()
        if interval == "1d":
            historical = data.get("historical", [])
        else:
            historical = data if isinstance(data, list) else []
        
        result = []
        cutoff = datetime.now() - timedelta(days=lookback_days)
        
        for item in historical:
            try:
                ts = datetime.strptime(item["date"].split()[0], "%Y-%m-%d")
                if ts < cutoff:
                    continue
                result.append(OHLCVData(
                    timestamp=ts, ticker=ticker.upper(), interval=interval,
                    open=float(item.get("open", 0)), high=float(item.get("high", 0)),
                    low=float(item.get("low", 0)), close=float(item.get("close", 0)),
                    volume=int(item.get("volume", 0)),
                    adj_close=float(item.get("adjClose", item.get("close", 0))),
                    source=self.SOURCE_NAME
                ))
            except (KeyError, ValueError):
                continue
        
        result.sort(key=lambda x: x.timestamp)
        return result


# =============================================================================
# POLYGON - FREE 5/min
# =============================================================================

POLYGON_AVAILABLE = bool(os.getenv("POLYGON_API_KEY", ""))


class PolygonConnector(DataConnector):
    """Polygon.io - premium data, FREE 5/min."""
    
    SOURCE_NAME = "polygon"
    BASE_URL = "https://api.polygon.io"
    SUPPORTED_INTERVALS = ["1m", "5m", "15m", "30m", "1h", "1d", "1w"]
    RATE_LIMIT_REQUESTS = 5
    RATE_LIMIT_WINDOW = 60
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv("POLYGON_API_KEY", "")
    
    @retry_with_backoff(max_retries=3, base_delay=2.0)
    def fetch_ohlcv(self, ticker: str, interval: str = "1d", lookback_days: int = 30) -> list[OHLCVData]:
        if not self.api_key:
            return []
        self.rate_limiter.wait_if_needed(ticker)
        
        # Map intervals
        timespan_map = {"1m": ("1", "minute"), "5m": ("5", "minute"),
                        "15m": ("15", "minute"), "30m": ("30", "minute"),
                        "1h": ("1", "hour"), "1d": ("1", "day"), "1w": ("1", "week")}
        multiplier, timespan = timespan_map.get(interval, ("1", "day"))
        
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
        
        logger.info(f"Fetching {ticker} from Polygon")
        url = f"{self.BASE_URL}/v2/aggs/ticker/{ticker.upper()}/range/{multiplier}/{timespan}/{start_date}/{end_date}"
        resp = requests.get(url, params={"apiKey": self.api_key, "adjusted": "true"}, timeout=30)
        
        if resp.status_code != 200:
            return []
        
        data = resp.json()
        result = []
        
        for item in data.get("results", []):
            try:
                result.append(OHLCVData(
                    timestamp=datetime.fromtimestamp(item["t"] / 1000),
                    ticker=ticker.upper(), interval=interval,
                    open=float(item["o"]), high=float(item["h"]),
                    low=float(item["l"]), close=float(item["c"]),
                    volume=int(item["v"]), source=self.SOURCE_NAME
                ))
            except (KeyError, ValueError):
                continue
        return result
    
    def fetch_news(self, ticker: str, lookback_days: int = 7) -> list[dict]:
        """Fetch news for ticker"""
        if not self.api_key:
            return []
        self.rate_limiter.wait_if_needed(ticker)
        
        resp = requests.get(f"{self.BASE_URL}/v2/reference/news", params={
            "ticker": ticker.upper(),
            "limit": 50,
            "apiKey": self.api_key
        }, timeout=30)
        
        return resp.json().get("results", []) if resp.status_code == 200 else []


# =============================================================================
# IEX CLOUD - FREE 50k/month
# =============================================================================

IEX_CLOUD_AVAILABLE = bool(os.getenv("IEX_CLOUD_API_KEY", ""))


class IEXCloudConnector(DataConnector):
    """IEX Cloud - premium data, FREE 50k/month."""
    
    SOURCE_NAME = "iex_cloud"
    BASE_URL = "https://cloud.iexapis.com/stable"
    SUPPORTED_INTERVALS = ["1d"]
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 60
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__()
        self.api_key = api_key or os.getenv("IEX_CLOUD_API_KEY", "")
    
    @retry_with_backoff(max_retries=3, base_delay=2.0)
    def fetch_ohlcv(self, ticker: str, interval: str = "1d", lookback_days: int = 30) -> list[OHLCVData]:
        if not self.api_key:
            return []
        self.rate_limiter.wait_if_needed(ticker)
        
        # Choose range based on lookback
        if lookback_days <= 5:
            range_param = "5d"
        elif lookback_days <= 30:
            range_param = "1m"
        elif lookback_days <= 90:
            range_param = "3m"
        elif lookback_days <= 180:
            range_param = "6m"
        else:
            range_param = "1y"
        
        logger.info(f"Fetching {ticker} from IEX Cloud")
        resp = requests.get(
            f"{self.BASE_URL}/stock/{ticker.upper()}/chart/{range_param}",
            params={"token": self.api_key},
            timeout=30
        )
        
        if resp.status_code != 200:
            return []
        
        data = resp.json()
        result = []
        
        for item in data:
            try:
                result.append(OHLCVData(
                    timestamp=datetime.strptime(item["date"], "%Y-%m-%d"),
                    ticker=ticker.upper(), interval=interval,
                    open=float(item.get("open", 0)), high=float(item.get("high", 0)),
                    low=float(item.get("low", 0)), close=float(item.get("close", 0)),
                    volume=int(item.get("volume", 0)),
                    adj_close=float(item.get("fClose", item.get("close", 0))),
                    source=self.SOURCE_NAME
                ))
            except (KeyError, ValueError):
                continue
        return result


# =============================================================================
# SINGLETON INSTANCES
# =============================================================================

# Primary (always available)
yfinance_connector = YFinanceConnector() if YFINANCE_AVAILABLE else None

# API-key based connectors
alpha_vantage_connector = AlphaVantageConnector() if ALPHA_VANTAGE_AVAILABLE else None
finnhub_connector = FinnhubConnector() if FINNHUB_AVAILABLE else None
twelve_data_connector = TwelveDataConnector() if TWELVE_DATA_AVAILABLE else None
fmp_connector = FMPConnector() if FMP_AVAILABLE else None
polygon_connector = PolygonConnector() if POLYGON_AVAILABLE else None
iex_cloud_connector = IEXCloudConnector() if IEX_CLOUD_AVAILABLE else None


# =============================================================================
# CONNECTOR REGISTRY
# =============================================================================

def get_available_connectors() -> list[DataConnector]:
    """Get list of all available (configured) connectors"""
    connectors = []
    if yfinance_connector:
        connectors.append(yfinance_connector)
    if alpha_vantage_connector:
        connectors.append(alpha_vantage_connector)
    if finnhub_connector:
        connectors.append(finnhub_connector)
    if twelve_data_connector:
        connectors.append(twelve_data_connector)
    if fmp_connector:
        connectors.append(fmp_connector)
    if polygon_connector:
        connectors.append(polygon_connector)
    if iex_cloud_connector:
        connectors.append(iex_cloud_connector)
    return connectors


def fetch_with_fallback(ticker: str, interval: str = "1d", lookback_days: int = 30) -> list[OHLCVData]:
    """
    Fetch OHLCV data with automatic fallback.
    
    Tries each available connector until one succeeds.
    """
    connectors = get_available_connectors()
    
    for connector in connectors:
        try:
            if interval in connector.SUPPORTED_INTERVALS:
                data = connector.fetch_ohlcv(ticker, interval, lookback_days)
                if data:
                    logger.info(f"Got {len(data)} bars from {connector.SOURCE_NAME}")
                    return data
        except Exception as e:
            logger.warning(f"{connector.SOURCE_NAME} failed: {e}")
            continue
    
    logger.error(f"All connectors failed for {ticker}")
    return []

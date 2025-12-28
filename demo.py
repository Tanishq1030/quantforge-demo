"""
QuantForge Demo - Smart Stock Data Fetching

Demonstrates the multi-source data connector with automatic fallback.
"""
from connectors import (
    fetch_with_fallback,
    yfinance_connector,
    get_available_connectors
)


def main():
    print("=" * 60)
    print("QuantForge Demo: Multi-Source Data Pipeline")
    print("=" * 60)
    
    # Show available connectors
    connectors = get_available_connectors()
    print(f"\n✅ Available Connectors: {len(connectors)}")
    for conn in connectors:
        print(f"   - {conn.SOURCE_NAME} (rate limit: {conn.RATE_LIMIT_REQUESTS}/{conn.RATE_LIMIT_WINDOW}s)")
    
    # Fetch data with automatic fallback
    print("\n📊 Fetching AAPL data (last 7 days) with auto-fallback...")
    data = fetch_with_fallback("AAPL", interval="1d", lookback_days=7)
    
    if data:
        print(f"\n✅ Got {len(data)} bars from {data[0].source}")
        print("\nLatest 5 bars:")
        for bar in data[-5:]:
            print(f"  {bar.timestamp.strftime('%Y-%m-%d')}: "
                  f"O=${bar.open:.2f} H=${bar.high:.2f} "
                  f"L=${bar.low:.2f} C=${bar.close:.2f} "
                  f"Vol={bar.volume:,}")
    else:
        print("❌ All connectors failed")
    
    # Direct connector usage
    print("\n" + "=" * 60)
    print("Direct yfinance Connector Usage")
    print("=" * 60)
    
    if yfinance_connector:
        print("\n📊 Fetching TSLA data (last 5 days)...")
        tsla_data = yfinance_connector.fetch_ohlcv("TSLA", interval="1d", lookback_days=5)
        
        if tsla_data:
            print(f"\n✅ Got {len(tsla_data)} bars")
            latest = tsla_data[-1]
            print(f"\nLatest close: ${latest.close:.2f}")
            print(f"Volume: {latest.volume:,}")
    
    print("\n" + "=" * 60)
    print("Demo Complete! ✨")
    print("=" * 60)


if __name__ == "__main__":
    main()

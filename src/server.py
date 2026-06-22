#!/usr/bin/env python3
import os
import yfinance as yf
from fastmcp import FastMCP

mcp = FastMCP("BIST Stock Data MCP Server")

BIST_SUFFIX = ".IS"

def _ensure_bist_ticker(ticker: str) -> str:
    if not ticker.upper().endswith(BIST_SUFFIX):
        ticker = ticker.upper() + BIST_SUFFIX
    return ticker

@mcp.tool(description="Get current price and basic information for a BIST stock")
def get_bist_stock_info(ticker: str) -> dict:
    """Fetch current BIST stock information from Yahoo Finance.
    Example: FROTO.IS (Ford Otosan), PGSUS.IS (Pegasus), ASELS.IS (Aselsan)
    """
    try:
        ticker = _ensure_bist_ticker(ticker)
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            "ticker": ticker,
            "name": info.get("longName", "N/A"),
            "current_price": info.get("currentPrice", "N/A"),
            "currency": info.get("currency", "TRY"),
            "market_cap": info.get("marketCap", "N/A"),
            "previous_close": info.get("previousClose", "N/A"),
            "open": info.get("open", "N/A"),
            "day_high": info.get("dayHigh", "N/A"),
            "day_low": info.get("dayLow", "N/A"),
            "volume": info.get("volume", "N/A"),
            "market": "BIST (Borsa Istanbul)",
        }
    except Exception as e:
        return {"error": f"Could not fetch data for {ticker}", "details": str(e)}

@mcp.tool(description="Get analyst recommendations and price targets for a BIST stock")
def get_analyst_recommendations(ticker: str) -> dict:
    """Fetch analyst consensus and price targets for a BIST stock."""
    try:
        ticker = _ensure_bist_ticker(ticker)
        stock = yf.Ticker(ticker)
        info = stock.info
        
        current_price = info.get("currentPrice")
        target_price = info.get("targetMeanPrice")
        recommendation = info.get("recommendationKey", "N/A")
        
        potential_return = None
        if current_price and target_price:
            potential_return = round(((target_price - current_price) / current_price) * 100, 2)
            
        return {
            "ticker": ticker,
            "recommendation": recommendation,
            "target_mean_price": target_price,
            "current_price": current_price,
            "potential_return_percent": potential_return,
            "currency": info.get("currency", "TRY")
        }
    except Exception as e:
        return {"error": f"Could not fetch recommendations for {ticker}", "details": str(e)}

@mcp.tool(description="Get latest KAP and news titles for a BIST stock")
def get_bist_news(ticker: str) -> dict:
    """Fetch aggregated news and KAP announcements from Yahoo Finance feed."""
    try:
        ticker = _ensure_bist_ticker(ticker)
        stock = yf.Ticker(ticker)
        news_list = stock.news
        
        formatted_news = []
        for item in news_list:
            formatted_news.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "publisher": item.get("publisher"),
                "provider_publish_time": item.get("providerPublishTime")
            })
            
        return {
            "ticker": ticker,
            "news": formatted_news,
            "count": len(formatted_news)
        }
    except Exception as e:
        return {"error": f"Could not fetch news for {ticker}", "details": str(e)}

@mcp.tool(description="Get historical price data for a BIST stock over a specified period")
def get_bist_historical_data(ticker: str, period: str = "1mo", interval: str = "1d") -> dict:
    """Fetch historical BIST stock data.
    period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, max
    interval: 1m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo
    """
    try:
        ticker = _ensure_bist_ticker(ticker)
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period, interval=interval)

        if hist.empty:
            return {"error": f"No historical data found for {ticker}", "ticker": ticker, "period": period}

        data_points = []
        for date, row in hist.iterrows():
            data_points.append({
                "date": date.strftime("%Y-%m-%d %H:%M:%S"),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]),
            })

        return {
            "ticker": ticker,
            "period": period,
            "interval": interval,
            "data_points": data_points,
            "count": len(data_points),
            "currency": "TRY",
        }
    except Exception as e:
        return {"error": f"Could not fetch historical data for {ticker}", "details": str(e)}

@mcp.tool(description="Compare multiple BIST stocks side by side")
def compare_bist_stocks(tickers: list) -> dict:
    """Compare multiple BIST stocks at once.
    Example: ["FROTO.IS", "PGSUS.IS", "ASELS.IS", "THYAO.IS"]
    """
    try:
        comparison = []
        for raw in tickers:
            t = _ensure_bist_ticker(raw)
            try:
                info = yf.Ticker(t).info
                comparison.append({
                    "ticker": t,
                    "name": info.get("longName", "N/A"),
                    "price": info.get("currentPrice", "N/A"),
                    "change_percent": info.get("regularMarketChangePercent", "N/A"),
                    "market_cap": info.get("marketCap", "N/A"),
                })
            except Exception as e:
                comparison.append({"ticker": t, "error": str(e)})

        return {"market": "BIST (Borsa Istanbul)", "comparison": comparison, "count": len(comparison)}
    except Exception as e:
        return {"error": "Could not compare stocks", "details": str(e)}

@mcp.tool(description="Get daily change and percentage change for a BIST stock")
def get_bist_daily_change(ticker: str) -> dict:
    """Get the daily change (price difference and percentage) for a BIST stock."""
    try:
        ticker = _ensure_bist_ticker(ticker)
        info = yf.Ticker(ticker).info
        current = info.get("currentPrice")
        previous = info.get("previousClose")

        if current and previous:
            change = current - previous
            pct = (change / previous) * 100
            return {
                "ticker": ticker,
                "name": info.get("longName", "N/A"),
                "current_price": round(current, 2),
                "previous_close": round(previous, 2),
                "change": round(change, 2),
                "change_percent": round(pct, 2),
                "currency": "TRY",
            }
        return {"error": "Missing price data", "ticker": ticker}
    except Exception as e:
        return {"error": f"Could not fetch daily change for {ticker}", "details": str(e)}

@mcp.tool(description="Get information about the BIST MCP server itself")
def get_server_info() -> dict:
    return {
        "server_name": "BIST Stock Data MCP Server",
        "version": "1.2.0",
        "description": "Real-time and historical BIST (Borsa Istanbul) stock data via Yahoo Finance",
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "market": "BIST (Borsa Istanbul)",
        "ticker_format": "TICKER.IS (e.g., FROTO.IS, PGSUS.IS, THYAO.IS)",
        "currency": "TRY",
    }

if __name__ == "__main__":
    # Dynamically bind port using PORT environment variable for Render (default to 10000)
    port = int(os.environ.get("PORT", 10000))
    # Bind to 0.0.0.0 to be accessible externally within the container/platform
    host = "0.0.0.0"
    print(f"Starting BIST Stock Data MCP server on {host}:{port}")
    # Using SSE transport for web deployment
    mcp.run(transport="sse", host=host, port=port)

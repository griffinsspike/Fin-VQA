"""
Fin-VQA Data Pipeline Module.
Handles all data fetching operations: OHLCV data, fundamental metrics, and news headlines.
Utilizes yfinance as primary source with Google News RSS as fallback for headlines.
"""

import logging
from datetime import datetime
from typing import Optional

import feedparser
import pandas as pd
import streamlit as st
import yfinance as yf

from src.config import CACHE_TTL_SECONDS, LOG_DATE_FORMAT, NEWS_COUNT

logger = logging.getLogger(__name__)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def fetch_stock_data(ticker: str, period: str = "1y") -> Optional[pd.DataFrame]:
    """
    Fetched OHLCV data for the given ticker via yfinance.

    Parameters
    ----------
    ticker : str
        Yahoo Finance ticker symbol (e.g., 'THYAO.IS').
    period : str
        Data period (e.g., '1mo', '3mo', '1y').

    Returns
    -------
    pd.DataFrame or None
        DataFrame with Open, High, Low, Close, Volume columns.
        Returned None if fetching failed.
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period, auto_adjust=True)

        if df.empty:
            logger.warning(f"No data was returned for ticker {ticker}.")
            return None

        # Cleaned column names for consistency
        df.index.name = "Date"
        df = df[["Open", "High", "Low", "Close", "Volume"]]
        df = df.dropna()

        logger.info(
            f"Successfully fetched {len(df)} records for {ticker} "
            f"(period={period}) at {datetime.now().strftime(LOG_DATE_FORMAT)}."
        )
        return df

    except Exception as e:
        logger.error(f"Failed to fetch stock data for {ticker}: {e}")
        return None


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def fetch_fundamentals(ticker: str) -> dict:
    """
    Fetched fundamental metrics for the given ticker.

    Returns a dictionary containing:
    - currentPrice, fiftyTwoWeekHigh, fiftyTwoWeekLow
    - trailingPE (F/K), priceToBook (PD/DD)
    - averageVolume, dividendYield, marketCap
    - shortName, sector, industry
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        fundamentals = {
            "shortName": info.get("shortName", ticker.replace(".IS", "")),
            "currentPrice": info.get("currentPrice") or info.get("regularMarketPrice", 0),
            "previousClose": info.get("previousClose", 0),
            "fiftyTwoWeekHigh": info.get("fiftyTwoWeekHigh", 0),
            "fiftyTwoWeekLow": info.get("fiftyTwoWeekLow", 0),
            "trailingPE": info.get("trailingPE", None),
            "forwardPE": info.get("forwardPE", None),
            "priceToBook": info.get("priceToBook", None),
            "averageVolume": info.get("averageVolume", 0),
            "dividendYield": info.get("dividendYield", None),
            "marketCap": info.get("marketCap", 0),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "beta": info.get("beta", None),
            "currency": info.get("currency", "TRY"),
            "website": info.get("website", ""),
            "logo_url": info.get("logo_url", ""),
        }

        logger.info(
            f"Fundamental metrics were fetched for {ticker} at "
            f"{datetime.now().strftime(LOG_DATE_FORMAT)}."
        )
        return fundamentals

    except Exception as e:
        logger.error(f"Failed to fetch fundamentals for {ticker}: {e}")
        return {
            "shortName": ticker.replace(".IS", ""),
            "currentPrice": 0,
            "previousClose": 0,
            "fiftyTwoWeekHigh": 0,
            "fiftyTwoWeekLow": 0,
            "trailingPE": None,
            "forwardPE": None,
            "priceToBook": None,
            "averageVolume": 0,
            "dividendYield": None,
            "marketCap": 0,
            "sector": "N/A",
            "industry": "N/A",
            "beta": None,
            "currency": "TRY",
            "website": "",
            "logo_url": "",
        }


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def fetch_news(ticker: str, count: int = NEWS_COUNT) -> list[dict]:
    """
    Fetched latest news headlines for the given ticker.
    Primary source: yfinance news API.
    Fallback: Google News RSS feed.

    Returns a list of dicts: [{title, link, published}]
    """
    headlines = []

    # ── Primary: yfinance news ──
    try:
        stock = yf.Ticker(ticker)
        news_data = stock.news

        if news_data:
            for item in news_data[:count]:
                # yfinance 1.3+ uses nested "content" structure
                content = item.get("content", item)
                provider = content.get("provider", {})
                click_url = content.get("clickThroughUrl", {})
                canonical_url = content.get("canonicalUrl", {})

                headline = {
                    "title": content.get("title", item.get("title", "No title")),
                    "link": (
                        click_url.get("url")
                        or canonical_url.get("url")
                        or item.get("link", "#")
                    ),
                    "published": content.get("pubDate", item.get("providerPublishTime", "")),
                    "source": provider.get("displayName", item.get("publisher", "Yahoo Finance")),
                }
                # Converted Unix timestamp if present
                if isinstance(headline["published"], (int, float)):
                    headline["published"] = datetime.fromtimestamp(
                        headline["published"]
                    ).strftime("%d.%m.%Y %H:%M")
                elif isinstance(headline["published"], str) and "T" in headline["published"]:
                    try:
                        dt = datetime.fromisoformat(headline["published"].replace("Z", "+00:00"))
                        headline["published"] = dt.strftime("%d.%m.%Y %H:%M")
                    except (ValueError, TypeError):
                        pass
                headlines.append(headline)

            if headlines:
                logger.info(
                    f"{len(headlines)} news headlines were fetched via yfinance for {ticker}."
                )
                return headlines[:count]

    except Exception as e:
        logger.warning(f"yfinance news fetch failed for {ticker}: {e}")

    # ── Fallback: Google News RSS ──
    try:
        clean_ticker = ticker.replace(".IS", "")
        rss_url = (
            f"https://news.google.com/rss/search?"
            f"q={clean_ticker}+borsa+hisse&hl=tr&gl=TR&ceid=TR:tr"
        )
        feed = feedparser.parse(rss_url)

        for entry in feed.entries[:count]:
            headline = {
                "title": entry.get("title", "No title"),
                "link": entry.get("link", "#"),
                "published": entry.get("published", ""),
                "source": "Google News",
            }
            headlines.append(headline)

        if headlines:
            logger.info(
                f"{len(headlines)} news headlines were fetched via Google News RSS for {ticker}."
            )

    except Exception as e:
        logger.error(f"Google News RSS fallback also failed for {ticker}: {e}")

    if not headlines:
        fallback_ticker = ticker.replace(".IS", "")
        headlines.append({
            "title": f"No recent news was found for {fallback_ticker}.",
            "link": "#",
            "published": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "source": "System",
        })

    return headlines[:count]


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def fetch_bist_overview(tickers: tuple) -> list:
    """Fetches price + volume snapshot for a list of tickers (pass as tuple for caching)."""
    results = []
    for tk in tickers:
        try:
            f = fetch_fundamentals(tk)
            p = f.get("currentPrice", 0)
            prev = f.get("previousClose", 0)
            vol = f.get("averageVolume", 0)
            chg = ((p - prev) / prev * 100) if prev else 0
            beta = f.get("beta") or 1.0
            results.append({
                "ticker": tk.replace(".IS", ""),
                "price": p,
                "change": chg,
                "avg_volume": vol,
                "beta": beta,
                "name": f.get("shortName", tk.replace(".IS", "")),
            })
        except Exception:
            pass
    return results


def format_fundamentals_text(fundamentals: dict) -> str:
    """
    Formatted fundamental metrics into a structured text block for LLM consumption.
    """
    pe = fundamentals.get("trailingPE")
    pe_str = f"{pe:.2f}" if pe else "N/A"

    fpe = fundamentals.get("forwardPE")
    fpe_str = f"{fpe:.2f}" if fpe else "N/A"

    pb = fundamentals.get("priceToBook")
    pb_str = f"{pb:.2f}" if pb else "N/A"

    div_yield = fundamentals.get("dividendYield")
    div_str = f"{div_yield * 100:.2f}%" if div_yield else "N/A"

    beta = fundamentals.get("beta")
    beta_str = f"{beta:.2f}" if beta else "N/A"

    mcap = fundamentals.get("marketCap", 0)
    if mcap >= 1e12:
        mcap_str = f"{mcap / 1e12:.2f}T TRY"
    elif mcap >= 1e9:
        mcap_str = f"{mcap / 1e9:.2f}B TRY"
    elif mcap >= 1e6:
        mcap_str = f"{mcap / 1e6:.2f}M TRY"
    else:
        mcap_str = f"{mcap:,.0f} TRY"

    text = f"""
═══════════════════════════════════════
  FUNDAMENTAL METRICS – {fundamentals.get('shortName', 'N/A')}
═══════════════════════════════════════
  Current Price    : {fundamentals.get('currentPrice', 0):,.2f} {fundamentals.get('currency', 'TRY')}
  Previous Close   : {fundamentals.get('previousClose', 0):,.2f} {fundamentals.get('currency', 'TRY')}
  52-Week High     : {fundamentals.get('fiftyTwoWeekHigh', 0):,.2f} {fundamentals.get('currency', 'TRY')}
  52-Week Low      : {fundamentals.get('fiftyTwoWeekLow', 0):,.2f} {fundamentals.get('currency', 'TRY')}
  ─────────────────────────────────────
  F/K (P/E Trailing) : {pe_str}
  F/K (P/E Forward)  : {fpe_str}
  PD/DD (P/B)        : {pb_str}
  Dividend Yield     : {div_str}
  Beta               : {beta_str}
  ─────────────────────────────────────
  Average Volume   : {fundamentals.get('averageVolume', 0):,.0f}
  Market Cap       : {mcap_str}
  Sector           : {fundamentals.get('sector', 'N/A')}
  Industry         : {fundamentals.get('industry', 'N/A')}
═══════════════════════════════════════
"""
    return text.strip()


def format_news_text(news: list[dict]) -> str:
    """
    Formatted news headlines into a structured text block for LLM consumption.
    """
    if not news:
        return "No recent news headlines were available."

    lines = ["═══ RECENT NEWS HEADLINES ═══"]
    for i, item in enumerate(news, 1):
        lines.append(
            f"  {i}. [{item.get('source', 'N/A')}] {item['title']} "
            f"({item.get('published', 'N/A')})"
        )
    lines.append("═════════════════════════════")

    return "\n".join(lines)

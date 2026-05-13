"""
Fin-VQA Technical Indicators Module.
Calculates RSI, Moving Averages, and other technical indicators for stock analysis.
"""

import logging

import numpy as np
import pandas as pd

from src.config import MA_LONG, MA_SHORT, RSI_PERIOD

logger = logging.getLogger(__name__)


def calculate_rsi(df: pd.DataFrame, period: int = RSI_PERIOD) -> pd.Series:
    """
    Calculated the Relative Strength Index (RSI) for the given OHLCV DataFrame.

    Uses the Exponential Moving Average (Wilder's smoothing) method.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with a 'Close' column.
    period : int
        RSI lookback period (default: 14).

    Returns
    -------
    pd.Series
        RSI values indexed by date.
    """
    try:
        delta = df["Close"].diff()

        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)

        # Wilder's smoothing (EMA with alpha = 1/period)
        avg_gain = gain.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1.0 / period, min_periods=period, adjust=False).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        # Handled edge cases
        rsi = rsi.replace([np.inf, -np.inf], np.nan).fillna(50)

        logger.info(f"RSI({period}) was calculated successfully ({len(rsi)} data points).")
        return rsi

    except Exception as e:
        logger.error(f"RSI calculation failed: {e}")
        return pd.Series(dtype=float)


def calculate_ma(df: pd.DataFrame, window: int) -> pd.Series:
    """
    Calculated Simple Moving Average (SMA) for the Close price.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with a 'Close' column.
    window : int
        Moving average window size.

    Returns
    -------
    pd.Series
        SMA values indexed by date.
    """
    try:
        ma = df["Close"].rolling(window=window, min_periods=1).mean()
        logger.info(f"MA({window}) was calculated successfully ({len(ma)} data points).")
        return ma
    except Exception as e:
        logger.error(f"MA({window}) calculation failed: {e}")
        return pd.Series(dtype=float)


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Added all technical indicators (RSI, MA20, MA50) to the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Raw OHLCV DataFrame.

    Returns
    -------
    pd.DataFrame
        DataFrame enriched with RSI, MA20, and MA50 columns.
    """
    if df is None or df.empty:
        logger.warning("Empty DataFrame was received; indicators were not added.")
        return df

    df = df.copy()
    df["RSI"] = calculate_rsi(df)
    df["MA20"] = calculate_ma(df, MA_SHORT)
    df["MA50"] = calculate_ma(df, MA_LONG)

    # ── Candle classification for Midas styling ──
    df["CandleType"] = "doji"
    body = abs(df["Close"] - df["Open"])
    total_range = df["High"] - df["Low"]
    # Classified as doji if body < 10% of total range
    doji_mask = body < (total_range * 0.1)
    df.loc[df["Close"] > df["Open"], "CandleType"] = "up"
    df.loc[df["Close"] < df["Open"], "CandleType"] = "down"
    df.loc[doji_mask, "CandleType"] = "doji"

    logger.info("All technical indicators were added to the DataFrame.")
    return df


def get_indicator_summary(df: pd.DataFrame) -> dict:
    """
    Generated a summary of current indicator values for display.

    Returns
    -------
    dict
        Latest RSI, MA20, MA50 values and their signals.
    """
    if df is None or df.empty:
        return {}

    latest = df.iloc[-1]
    current_price = latest["Close"]

    rsi_val = latest.get("RSI", 50)
    ma20_val = latest.get("MA20", current_price)
    ma50_val = latest.get("MA50", current_price)

    # RSI signal
    if rsi_val >= 70:
        rsi_signal = "Aşırı Alım (Overbought)"
    elif rsi_val <= 30:
        rsi_signal = "Aşırı Satım (Oversold)"
    else:
        rsi_signal = "Nötr (Neutral)"

    # MA crossover signal
    if ma20_val > ma50_val:
        ma_signal = "Yükseliş Trendi (Bullish Cross)"
    elif ma20_val < ma50_val:
        ma_signal = "Düşüş Trendi (Bearish Cross)"
    else:
        ma_signal = "Nötr (Neutral)"

    # Price vs MA
    price_vs_ma20 = "Üstünde" if current_price > ma20_val else "Altında"
    price_vs_ma50 = "Üstünde" if current_price > ma50_val else "Altında"

    return {
        "rsi": round(rsi_val, 2),
        "rsi_signal": rsi_signal,
        "ma20": round(ma20_val, 2),
        "ma50": round(ma50_val, 2),
        "ma_signal": ma_signal,
        "price_vs_ma20": price_vs_ma20,
        "price_vs_ma50": price_vs_ma50,
        "current_price": round(current_price, 2),
    }

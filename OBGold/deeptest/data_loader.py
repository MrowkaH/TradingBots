from __future__ import annotations

import warnings
from dataclasses import dataclass
from typing import Optional

import pandas as pd
import numpy as np

try:
    import yfinance as yf  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    yf = None  # type: ignore


@dataclass
class DataConfig:
    symbol: str = "GC=F"  # Yahoo Finance gold futures; alternative: "XAUUSD=X"
    start: str = "2010-01-01"
    end: Optional[str] = None  # None = today
    timeframe: str = "1d"  # yfinance interval
    csv_path: Optional[str] = None


def _from_yfinance(cfg: DataConfig) -> pd.DataFrame:
    if yf is None:
        raise RuntimeError("yfinance not installed; install it or provide csv_path")
    ticker = yf.Ticker(cfg.symbol)
    df = ticker.history(start=cfg.start, end=cfg.end, interval=cfg.timeframe, auto_adjust=False)
    if df.empty:
        raise RuntimeError(f"No data returned for {cfg.symbol}")
    df = df.rename(columns={c: c.capitalize() for c in df.columns})
    df.index = pd.to_datetime(df.index)
    return df[[c for c in ["Open", "High", "Low", "Close", "Volume"] if c in df.columns]]


def _from_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Try common schemas
    if "Date" in df.columns:
        idx = pd.to_datetime(df["Date"])  # raises on failure
        df = df.set_index(idx).drop(columns=["Date"])
    elif df.columns[0].lower() in {"date", "datetime", "time"}:
        idx = pd.to_datetime(df.iloc[:, 0])
        df = df.set_index(idx).drop(columns=[df.columns[0]])
    df.index.name = "Date"
    # Ensure standard columns if present
    rename_map = {"open": "Open", "high": "High", "low": "Low", "close": "Close", "adj close": "Adj Close", "volume": "Volume"}
    df = df.rename(columns={k: rename_map[k.lower()] for k in list(df.columns) if k.lower() in rename_map})
    return df


def _synthetic(n: int = 3000, start_price: float = 1500.0, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    # Geometric Brownian motion like series
    mu = 0.0001
    sigma = 0.01
    rets = rng.normal(mu, sigma, size=n)
    prices = start_price * np.exp(np.cumsum(rets))
    idx = pd.date_range("2010-01-01", periods=n, freq="B")
    close = pd.Series(prices, index=idx)
    high = close * (1 + rng.uniform(0, 0.01, size=n))
    low = close * (1 - rng.uniform(0, 0.01, size=n))
    open_ = close.shift(1).fillna(close.iloc[0])
    vol = rng.integers(1e3, 1e5, size=n)
    df = pd.DataFrame({"Open": open_, "High": high, "Low": low, "Close": close, "Volume": vol}, index=idx)
    return df


def load_data(cfg: DataConfig) -> pd.DataFrame:
    """Load OHLCV and compute returns.

    Returns DataFrame with columns: Open, High, Low, Close, Volume, Ret (log), RetSimple
    Index is DatetimeIndex (UTC-naive).
    """
    if cfg.csv_path:
        df = _from_csv(cfg.csv_path)
    else:
        try:
            df = _from_yfinance(cfg)
        except Exception as e:
            warnings.warn(f"Falling back to synthetic data due to: {e}")
            df = _synthetic()

    df = df.sort_index()
    df = df[~df.index.duplicated(keep="last")]
    # Fill minimal gaps sensibly
    df = df.ffill().bfill()
    df["RetSimple"] = df["Close"].pct_change().fillna(0.0)
    # Log return; guard against non-finite values
    df["Ret"] = np.log1p(df["RetSimple"]).replace([np.inf, -np.inf], 0.0).fillna(0.0)
    return df

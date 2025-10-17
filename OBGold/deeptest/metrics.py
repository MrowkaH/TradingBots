from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd


TRADING_DAYS = 252


@dataclass
class Performance:
    cagr: float
    sharpe: float
    sortino: float
    vol: float
    max_dd: float
    max_dd_days: int
    calmar: float
    win_rate: float
    avg_win: float
    avg_loss: float
    trades: int


def drawdown(equity: pd.Series) -> pd.Series:
    peak = equity.cummax()
    dd = equity / peak - 1.0
    return dd


def compute_performance(equity: pd.Series, returns: pd.Series) -> Performance:
    equity = equity.dropna()
    returns = returns.dropna()
    if len(equity) == 0:
        raise ValueError("empty equity curve")
    total_return = equity.iloc[-1] / equity.iloc[0] - 1
    years = max((equity.index[-1] - equity.index[0]).days / 365.25, 1e-9)
    cagr = (1 + total_return) ** (1 / years) - 1
    vol = returns.std(ddof=0) * np.sqrt(TRADING_DAYS)
    sharpe = (returns.mean() * TRADING_DAYS) / (vol + 1e-12)
    downside = returns.where(returns < 0, 0.0)
    downside_vol = downside.std(ddof=0) * np.sqrt(TRADING_DAYS)
    sortino = (returns.mean() * TRADING_DAYS) / (downside_vol + 1e-12)
    dd = drawdown(equity)
    max_dd = dd.min()
    # duration
    dd_is = dd != 0
    max_dd_days = 0
    cur = 0
    for flag in dd_is:
        if flag:
            cur += 1
            max_dd_days = max(max_dd_days, cur)
        else:
            cur = 0
    calmar = (returns.mean() * TRADING_DAYS) / (abs(max_dd) + 1e-12)
    # wins/losses by sign of return when position != 0
    nonzero = returns[returns != 0]
    wins = nonzero[nonzero > 0]
    losses = nonzero[nonzero < 0]
    win_rate = float(len(wins)) / max(len(nonzero), 1)
    avg_win = wins.mean() if len(wins) else 0.0
    avg_loss = losses.mean() if len(losses) else 0.0
    # trades approximated by turnover half-count (entry+exit = 2)
    trades = int((returns.abs() > 0).sum())
    return Performance(
        cagr=float(cagr),
        sharpe=float(sharpe),
        sortino=float(sortino),
        vol=float(vol),
        max_dd=float(max_dd),
        max_dd_days=int(max_dd_days),
        calmar=float(calmar),
        win_rate=float(win_rate),
        avg_win=float(avg_win),
        avg_loss=float(avg_loss),
        trades=int(trades),
    )


def to_dict(p: Performance) -> Dict[str, float]:
    return {
        "CAGR": p.cagr,
        "Sharpe": p.sharpe,
        "Sortino": p.sortino,
        "Vol": p.vol,
        "MaxDD": p.max_dd,
        "MaxDD_Days": float(p.max_dd_days),
        "Calmar": p.calmar,
        "WinRate": p.win_rate,
        "AvgWin": p.avg_win,
        "AvgLoss": p.avg_loss,
        "Trades": float(p.trades),
    }

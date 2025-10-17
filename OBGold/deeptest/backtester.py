from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd
import numpy as np


@dataclass
class CostModel:
    commission_bps: float = 0.0  # round-trip per trade, applied on turnover
    slippage_bps: float = 0.0  # per trade, proxy via |position change|


@dataclass
class BacktestResult:
    equity: pd.Series
    returns: pd.Series
    position: pd.Series
    turnover: pd.Series
    costs: pd.Series


def run_backtest(df: pd.DataFrame, position: pd.Series, cost: Optional[CostModel] = None, starting_equity: float = 1.0) -> BacktestResult:
    """Vectorized backtest on Close-to-Close returns.

    - position: target position applied for holding period t->t+1
    - returns are simple returns df['RetSimple']
    Costs modeled by turnover = |pos_t - pos_{t-1}|.
    """
    cost = cost or CostModel()
    df = df.copy()
    ret = df.get("RetSimple")
    if ret is None or ret.isna().all():
        raise ValueError("DataFrame must include RetSimple column; use data_loader.load_data")
    pos = position.reindex(df.index).fillna(0.0).astype(float)
    pos_shift = pos.shift(1).fillna(0.0)
    # Apply returns with previous position for realistic fill at close
    pnl = pos_shift * ret
    turnover = (pos - pos_shift).abs()
    per_trade_bps = cost.commission_bps + cost.slippage_bps
    costs = turnover * (per_trade_bps / 1e4)
    net_ret = pnl - costs
    equity = (1 + net_ret).cumprod() * starting_equity
    return BacktestResult(
        equity=equity,
        returns=net_ret,
        position=pos,
        turnover=turnover,
        costs=costs,
    )

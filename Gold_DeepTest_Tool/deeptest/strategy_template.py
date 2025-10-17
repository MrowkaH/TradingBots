from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Any

import pandas as pd


StrategyFn = Callable[[pd.DataFrame, Dict[str, Any]], pd.Series]


@dataclass(frozen=True)
class StrategySpec:
    name: str
    params: Dict[str, Any]
    fn: StrategyFn


def ma_cross(df: pd.DataFrame, params: Dict[str, Any]) -> pd.Series:
    """Simple moving-average crossover strategy on Close.

    params:
      - fast: int
      - slow: int
      - neutral_zone: float (bps), optional; if abs(spread) < nz -> keep prior position
    Returns target position in {-1, 0, 1}.
    """
    fast = int(params.get("fast", 20))
    slow = int(params.get("slow", 100))
    nz_bps = float(params.get("neutral_zone", 0.0))
    close = df["Close"].astype(float)
    ma_f = close.rolling(fast, min_periods=fast).mean()
    ma_s = close.rolling(slow, min_periods=slow).mean()
    spread = (ma_f - ma_s) / ma_s
    pos = pd.Series(0, index=df.index, dtype=float)
    pos = pos.where(spread.isna(), pos)
    buy = spread > (nz_bps / 1e4)
    sell = spread < -(nz_bps / 1e4)
    pos = pos.mask(buy, 1.0)
    pos = pos.mask(sell, -1.0)
    pos = pos.replace(0, pd.NA).ffill().fillna(0.0)
    return pos.clip(-1, 1)


BUILT_IN_STRATEGIES: Dict[str, StrategyFn] = {
    "ma_cross": ma_cross,
}

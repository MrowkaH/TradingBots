from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Dict, Any, Iterable, List, Tuple

import numpy as np
import pandas as pd

from .backtester import run_backtest, CostModel
from .metrics import compute_performance, to_dict
from .strategy_template import StrategyFn


@dataclass
class WalkForwardConfig:
    train_years: int = 3
    test_years: int = 1
    step_years: int = 1


def _year_slices(idx: pd.DatetimeIndex, years: int) -> List[Tuple[pd.Timestamp, pd.Timestamp]]:
    start = idx.min()
    end = idx.max()
    slices = []
    cur = start
    while cur < end:
        stop = cur + pd.DateOffset(years=years)
        slices.append((cur, min(stop, end)))
        cur = stop
    return slices


def grid_search(df: pd.DataFrame, strat: StrategyFn, grid: Dict[str, Iterable[Any]], cost: CostModel) -> Tuple[Dict[str, Any], Dict[str, float]]:
    keys = list(grid.keys())
    best: Tuple[Dict[str, Any], Dict[str, float]] | None = None
    for values in product(*grid.values()):
        params = dict(zip(keys, values))
        pos = strat(df, params)
        res = run_backtest(df, pos, cost)
        perf = compute_performance(res.equity, res.returns)
        perf_d = to_dict(perf)
        if best is None or perf_d["CAGR"] > best[1]["CAGR"]:
            best = (params, perf_d)
    assert best is not None
    return best


def walk_forward(df: pd.DataFrame, strat: StrategyFn, grid: Dict[str, Iterable[Any]], cost: CostModel, cfg: WalkForwardConfig) -> pd.DataFrame:
    idx = df.index
    train_slices = _year_slices(idx, cfg.step_years)
    rows = []
    for i in range(0, len(train_slices)):
        train_start = train_slices[i][0]
        train_end = train_start + pd.DateOffset(years=cfg.train_years)
        test_end = train_end + pd.DateOffset(years=cfg.test_years)
        if train_end >= idx.max() or train_start >= idx.max():
            break
        df_train = df.loc[(df.index >= train_start) & (df.index < train_end)]
        df_test = df.loc[(df.index >= train_end) & (df.index < min(test_end, idx.max()))]
        if len(df_train) < 50 or len(df_test) < 20:
            continue
        best_params, _ = grid_search(df_train, strat, grid, cost)
        pos = strat(df_test, best_params)
        res = run_backtest(df_test, pos, cost)
        perf = to_dict(compute_performance(res.equity, res.returns))
        rows.append({
            "train_start": train_start,
            "train_end": train_end,
            "test_end": min(test_end, idx.max()),
            "params": best_params,
            **perf,
        })
    return pd.DataFrame(rows)


def permutation_test(df: pd.DataFrame, strat: StrategyFn, params: Dict[str, Any], cost: CostModel, n_iter: int = 500, block: int = 5, seed: int = 7) -> Dict[str, float]:
    """Shuffle returns in blocks to get p-value for performance under null."""
    rng = np.random.default_rng(seed)
    pos = strat(df, params)
    res_true = run_backtest(df, pos, cost)
    perf_true = to_dict(compute_performance(res_true.equity, res_true.returns))
    rets = df["RetSimple"].values.astype(float)
    n = len(rets)
    block = max(1, int(block))
    blocks = int(np.ceil(n / block))
    stats = []
    for _ in range(n_iter):
        order = rng.permutation(blocks)
        reshuffled = np.concatenate([rets[i*block:(i+1)*block] for i in order])[:n]
        df_shuf = df.copy()
        df_shuf["RetSimple"] = reshuffled
        res = run_backtest(df_shuf, pos, cost)
        perf = to_dict(compute_performance(res.equity, res.returns))
        stats.append(perf["CAGR"])
    cagr_true = perf_true["CAGR"]
    p_value = float((np.sum(np.array(stats) >= cagr_true) + 1) / (n_iter + 1))
    return {"CAGR_true": cagr_true, "p_value": p_value}


def bootstrap_ci(df: pd.DataFrame, strat: StrategyFn, params: Dict[str, Any], cost: CostModel, n_iter: int = 500, block: int = 5, seed: int = 42, alpha: float = 0.05) -> Dict[str, float]:
    rng = np.random.default_rng(seed)
    pos = strat(df, params)
    rets = df["RetSimple"].values.astype(float)
    n = len(rets)
    block = max(1, int(block))
    # Precompute variable-length blocks using starts
    starts = list(range(0, n, block))
    segments = [rets[s: min(s + block, n)] for s in starts]
    seg_count = len(segments)
    cagr_list = []
    for _ in range(n_iter):
        boot_parts = []
        total_len = 0
        # Sample with replacement until we have at least n points
        while total_len < n:
            i = int(rng.integers(0, seg_count))
            seg = segments[i]
            boot_parts.append(seg)
            total_len += len(seg)
        boot = np.concatenate(boot_parts)[:n]
        df_b = df.copy()
        df_b["RetSimple"] = boot
        res = run_backtest(df_b, pos, cost)
        perf = to_dict(compute_performance(res.equity, res.returns))
        cagr_list.append(perf["CAGR"])
    lower = float(np.quantile(cagr_list, alpha/2))
    upper = float(np.quantile(cagr_list, 1 - alpha/2))
    return {"CAGR_CI_low": lower, "CAGR_CI_high": upper}

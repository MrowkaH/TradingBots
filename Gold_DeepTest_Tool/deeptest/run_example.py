from __future__ import annotations

import pprint

from .data_loader import load_data, DataConfig
from .strategy_template import BUILT_IN_STRATEGIES
from .backtester import CostModel, run_backtest
from .metrics import compute_performance, to_dict
from .deep_test import grid_search, walk_forward, permutation_test, bootstrap_ci, WalkForwardConfig


def main():
    cfg = DataConfig(symbol="GC=F", start="2015-01-01", timeframe="1d")
    df = load_data(cfg)
    strat = BUILT_IN_STRATEGIES["ma_cross"]
    grid = {"fast": [10, 20, 30], "slow": [80, 100, 150], "neutral_zone": [0, 5, 10]}
    cost = CostModel(commission_bps=1.0, slippage_bps=2.0)

    print("= Grid search on full sample =")
    best_params, best_perf = grid_search(df, strat, grid, cost)
    pprint.pprint({"best_params": best_params, "perf": best_perf})

    print("\n= Walk-forward =")
    wf = walk_forward(df, strat, grid, cost, WalkForwardConfig(train_years=3, test_years=1, step_years=1))
    print(wf.tail(10))
    print({"WF_mean_CAGR": wf["CAGR"].mean(), "WF_median_CAGR": wf["CAGR"].median()})

    print("\n= Permutation test (CAGR p-value) =")
    perm = permutation_test(df, strat, best_params, cost, n_iter=200, block=5)
    pprint.pprint(perm)

    print("\n= Bootstrap CI (CAGR) =")
    ci = bootstrap_ci(df, strat, best_params, cost, n_iter=200, block=5)
    pprint.pprint(ci)

    # Final equity on full sample with best params
    pos = strat(df, best_params)
    res = run_backtest(df, pos, cost)
    perf = to_dict(compute_performance(res.equity, res.returns))
    pprint.pprint({"final_perf": perf, "final_equity": float(res.equity.iloc[-1])})


if __name__ == "__main__":
    main()

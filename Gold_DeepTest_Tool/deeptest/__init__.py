"""
Gold strategy deep test harness.

Modules:
- data_loader: Load XAUUSD/GC=F data from yfinance, CSV, or synthetic.
- strategy_template: Contract and example strategy to plug your own logic.
- backtester: Vectorized PnL, costs, equity.
- metrics: Robust performance statistics.
- deep_test: Walk-forward, grid search, permutation test, bootstrap CI.
"""

from . import data_loader, strategy_template, backtester, metrics, deep_test

__all__ = [
    "data_loader",
    "strategy_template",
    "backtester",
    "metrics",
    "deep_test",
]

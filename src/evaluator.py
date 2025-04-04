# src/evaluator.py

import numpy as np
import pandas as pd

def evaluate(trade_log: pd.DataFrame, initial_equity: float = 1.0):
    pnl = trade_log["realized_pnl"] + trade_log["unrealized_pnl"]
    equity = trade_log["equity"].iloc[0] + pnl.cumsum()

    total_return = trade_log["equity"].iloc[-1] - trade_log["equity"].iloc[0]
    sharpe_ratio = pnl.mean() / pnl.std() * np.sqrt(252) if pnl.std() > 0 else 0
    max_drawdown = (equity.cummax() - equity).max()

    metrics = {
        "Total Return": total_return,
        "Sharpe Ratio": sharpe_ratio,
        "Max Drawdown": max_drawdown,
        "Number of Trades": len(trade_log),
        "Average Trade PnL": pnl.mean()
    }

    return metrics

def print_metrics(metrics: dict, title="Strategy Evaluation"):
    print(f"\n=== {title} ===")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")
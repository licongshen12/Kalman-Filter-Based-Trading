# scripts/backtest.py

import pandas as pd
from src.kalman_filter import KalmanFilter
from src.backtest import run_kalman_backtest
from src.evaluator import evaluate, print_metrics

def main():
    # ✅ Step 1: Load data
    df_perp = pd.read_csv("data/processed/btc_usdt_processed.csv", parse_dates=["timestamp"])
    df_3m = pd.read_csv("data/processed/btc_3m_processed.csv", parse_dates=["timestamp"])

    # ✅ Step 2: Merge on timestamp
    df = pd.merge(
        df_perp[['timestamp', 'close']],
        df_3m[['timestamp', 'close']],
        on='timestamp',
        suffixes=('_perp', '_3m')
    )

    df.rename(columns={'close_perp': 'btc_perp', 'close_3m': 'btc_3m'}, inplace=True)
    df.set_index("timestamp", inplace=True)

    # ✅ Step 3: Check data sanity
    print("Merged data preview:")
    print(df.head())
    print("Shape:", df.shape)

    # ✅ Step 4: Run backtest
    trade_log = run_kalman_backtest(df, KalmanFilter)

    # ✅ Step 5: Check result
    if trade_log.empty:
        print("⚠️ No trades were generated.")
        return

    print("✅ Trade log preview:")
    print(trade_log.head())

    # ✅ Step 6: Evaluate
    metrics = evaluate(trade_log)
    print_metrics(metrics, title="Standard Kalman Filter")


if __name__ == "__main__":
    main()
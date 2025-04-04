import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def run_kalman_backtest(df, kalman_class, z_entry=0.8, z_exit=0.8, initial_capital=100000.0, trade_notional=100000.0):
    """
    Run a backtest for a mean-reversion strategy using the Kalman filter on two assets (BTC Perpetual and BTC 3M).
    - Entries and exits are determined by Z-scores.
    - Positions are sized using the hedge ratio (β₁).

    Parameters:
    df (DataFrame): The dataframe containing BTC perpetual and BTC 3M data.
    kalman_class: The Kalman filter class to use for calculating the spread and hedge ratio.
    z_entry (float): The Z-score threshold to enter trades.
    z_exit (float): The Z-score threshold to exit trades.
    initial_capital (float): The initial amount of capital available for trading.
    trade_notional (float): The size of each trade.

    Returns:
    pd.DataFrame: A dataframe containing the trade logs and the results of the backtest.
    """
    model = kalman_class()  # Instantiate the Kalman filter model
    df = df.copy()  # Work on a copy of the input dataframe
    spreads = []  # List to store the calculated spreads
    hedge_ratios = []  # List to store the calculated hedge ratios (β₁)

    prev_beta_sign = None  # Initialize for detecting sign flips of hedge ratio

    # Step 1: Use Kalman Filter to estimate spread and hedge ratio
    for i, (_, row) in enumerate(df.iterrows()):
        y = row['btc_3m']  # BTC 3M price
        x = row['btc_perp']  # BTC Perpetual price
        _, e = model.update(y, x)  # Update Kalman filter to calculate spread and residual (error)
        beta_1 = model.beta[1]  # Hedge ratio (β₁)

        # Log sign flips of the hedge ratio (this helps in detecting any changes in market dynamics)
        current_sign = np.sign(beta_1)
        if prev_beta_sign is not None and current_sign != prev_beta_sign:
            print(f"⚠️ Hedge ratio flipped at {row.name}: β₁ changed sign to {beta_1:.5f}")
        prev_beta_sign = current_sign

        spreads.append(e)  # Append the spread (error term)
        hedge_ratios.append(beta_1)  # Append the hedge ratio (β₁)

    # Add calculated spread, hedge ratio, and Z-score to the dataframe
    df['spread'] = spreads
    df['hedge_ratio'] = hedge_ratios
    df['zscore'] = (df['spread'] - df['spread'].rolling(40).mean()) / df['spread'].rolling(40).std()
    df.dropna(inplace=True)  # Drop NaN values after calculating Z-score

    # Initialize trading variables
    position = 0  # 0: no position, 1: long position, -1: short position
    equity = initial_capital  # Starting capital
    trade_log = []  # List to store trade logs

    entry_price_3m = 0
    entry_price_perp = 0
    entry_hedge_ratio = 1

    # Step 2: Iterate through the data to simulate trading
    for i in range(1, len(df)):
        row = df.iloc[i]  # Current row of data
        prev = df.iloc[i - 1]  # Previous row of data

        entry_flag = False  # Flag indicating if an entry was made
        exit_flag = False  # Flag indicating if an exit was made
        unrealized_pnl = 0  # The unrealized profit/loss for the current position
        realized_pnl = 0  # The realized profit/loss after exiting a trade

        beta_1 = row['hedge_ratio']  # Get the current hedge ratio (β₁)

        # Step 3: Skip trading if hedge ratio is negative or too small
        if beta_1 <= 0 or abs(beta_1) < 0.05:
            continue

        # Step 4: Entry conditions for long or short positions
        if position == 0:
            # Long entry condition: Z-score drops below the negative threshold (buy the spread)
            if row['zscore'] < -z_entry:
                position = 1  # Enter long position
                entry_flag = True  # Mark that an entry signal was triggered
                entry_price_3m = row['btc_3m']  # Set the entry price for BTC 3M
                entry_price_perp = row['btc_perp']  # Set the entry price for BTC Perpetual
                entry_hedge_ratio = beta_1  # Set the hedge ratio for the position
            # Short entry condition: Z-score rises above the positive threshold (sell the spread)
            elif row['zscore'] > z_entry:
                position = -1  # Enter short position
                entry_flag = True  # Mark that an entry signal was triggered
                entry_price_3m = row['btc_3m']  # Set the entry price for BTC 3M
                entry_price_perp = row['btc_perp']  # Set the entry price for BTC Perpetual
                entry_hedge_ratio = beta_1  # Set the hedge ratio for the position

        # Step 5: Exit condition for long positions
        elif position == 1:
            exit_price_3m = row['btc_3m']
            exit_price_perp = row['btc_perp']
            long_qty = trade_notional / entry_price_3m  # Position size for long trade
            short_qty = (trade_notional * entry_hedge_ratio) / entry_price_perp  # Position size for short trade

            unrealized_pnl = long_qty * (exit_price_3m - entry_price_3m) + \
                             short_qty * (entry_price_perp - exit_price_perp)  # Calculate unrealized PnL

            # Exit long position if Z-score is above the negative exit threshold
            if row['zscore'] < z_exit:
                position = 0  # Close the position
                realized_pnl = unrealized_pnl  # Capture the realized profit/loss
                equity += realized_pnl  # Add realized PnL to equity
                unrealized_pnl = 0  # Reset unrealized PnL
                exit_flag = True  # Mark that an exit signal was triggered

        # Step 6: Exit condition for short positions
        elif position == -1:
            exit_price_3m = row['btc_3m']
            exit_price_perp = row['btc_perp']
            short_qty = trade_notional / entry_price_3m  # Position size for short trade
            long_qty = (trade_notional * entry_hedge_ratio) / entry_price_perp  # Position size for long trade

            unrealized_pnl = short_qty * (entry_price_3m - exit_price_3m) + \
                             long_qty * (exit_price_perp - entry_price_perp)  # Calculate unrealized PnL

            # Exit short position if Z-score is below the positive exit threshold
            if row['zscore'] > -z_exit:
                position = 0  # Close the position
                realized_pnl = unrealized_pnl  # Capture the realized profit/loss
                equity += realized_pnl  # Add realized PnL to equity
                unrealized_pnl = 0  # Reset unrealized PnL
                exit_flag = True  # Mark that an exit signal was triggered

        # Step 7: Store trade data in the trade log
        trade_log.append({
            'timestamp': row.name,
            'position': position,  # Current position (long, short, or none)
            'zscore': row['zscore'],  # Current Z-score
            'spread': row['spread'],  # Current spread
            'hedge_ratio': beta_1,  # Current hedge ratio (β₁)
            'realized_pnl': realized_pnl,  # Realized profit/loss from exits
            'unrealized_pnl': unrealized_pnl,  # Unrealized profit/loss from open positions
            'equity': equity,  # Current equity after trade
            'entry_signal': entry_flag,  # Entry signal flag
            'exit_signal': exit_flag  # Exit signal flag
        })

    # Step 8: Return the dataframe of trade logs and results
    return pd.DataFrame(trade_log)
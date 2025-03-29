import os
import ccxt
import pandas as pd
import requests
from datetime import datetime
from dotenv import load_dotenv

# Run this from the root folder:
# $ python src/data_loader.py

# Load API keys
load_dotenv()

# Paths (relative to project root)
RAW_DATA_PATH = "data/raw/"
PROCESSED_DATA_PATH = "data/processed/"


def load_binance_data(symbol: str, timeframe: str = "1m", limit: int = 1000) -> pd.DataFrame:
    """
    Fetch historical OHLCV data from Binance using CCXT.

    Args:
        symbol (str): Trading pair, e.g., 'BTC/USDT'.
        timeframe (str): Timeframe (e.g., '1m', '5m', '1h').
        limit (int): Number of bars to fetch (max 1000 per call).

    Returns:
        pd.DataFrame: DataFrame of OHLCV data.
    """
    binance = ccxt.binance({
        'apiKey': os.getenv("BINANCE_API_KEY"),
        'secret': os.getenv("BINANCE_API_SECRET"),
    })

    ohlcv = binance.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df


def load_deribit_3m_data(instrument_name="BTC-27JUN25", resolution="1", count=1000) -> pd.DataFrame:
    """
    Fetch OHLCV data from Deribit for BTC futures using their TradingView API.
    Now includes required 'start_timestamp' param.
    """
    end_time = int(datetime.utcnow().timestamp() * 1000)  # now in ms
    duration_minutes = int(count) * int(resolution)
    start_time = end_time - duration_minutes * 60 * 1000  # ms

    url = "https://www.deribit.com/api/v2/public/get_tradingview_chart_data"
    params = {
        "instrument_name": instrument_name,
        "resolution": resolution,
        "start_timestamp": start_time,
        "end_timestamp": end_time
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "result" not in data:
        raise ValueError(f"❌ Deribit API error: {data.get('error', 'No result key in response')}")

    result = data["result"]
    df = pd.DataFrame({
        "timestamp": pd.to_datetime(result["ticks"], unit="ms"),
        "open": result["open"],
        "high": result["high"],
        "low": result["low"],
        "close": result["close"],
        "volume": result["volume"]
    })
    df.set_index("timestamp", inplace=True)
    return df


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df[~df.index.duplicated()]
    df = df.sort_index()
    return df


def save_raw_data(df: pd.DataFrame, filename: str):
    os.makedirs(RAW_DATA_PATH, exist_ok=True)
    df.to_csv(os.path.join(RAW_DATA_PATH, filename))
    print(f"Saved raw data to {RAW_DATA_PATH}{filename}")


def save_processed_data(df: pd.DataFrame, filename: str):
    os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)
    df.to_csv(os.path.join(PROCESSED_DATA_PATH, filename))
    print(f"Saved processed data to {PROCESSED_DATA_PATH}{filename}")


if __name__ == "__main__":
    # --- Load BTC/USDT perpetual from Binance ---
    df_perp = load_binance_data("BTC/USDT", timeframe="1m", limit=1000)
    save_raw_data(df_perp, "btc_usdt_raw.csv")

    df_perp_clean = preprocess_data(df_perp)
    save_processed_data(df_perp_clean, "btc_usdt_processed.csv")

    # --- Load BTC-3M futures from Deribit ---
    df_3m = load_deribit_3m_data(instrument_name="BTC-27JUN25", resolution="1", count=1000)
    save_raw_data(df_3m, "btc_3m_raw.csv")

    df_3m_clean = preprocess_data(df_3m)
    save_processed_data(df_3m_clean, "btc_3m_processed.csv")
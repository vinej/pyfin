import yfinance as yf
import polars as pl
import pandas as pd
from src.config.settings import RAW_DATA

def fetch_data(symbol="AAPL", start="2020-01-01"):
    df = yf.download(symbol, start=start)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    pl_df = pl.from_pandas(df.reset_index())
    pl_df.write_parquet(RAW_DATA / f"{symbol}.parquet")

    print(f"Saved {symbol} data to {RAW_DATA / f'{symbol}.parquet'}")
    return pl_df

import yfinance as yf
import polars as pl
import pandas as pd
from src.config.settings import RAW_DATA

def fetch_data(symbol="AAPL", start="2020-01-01"):
    df = yf.download(symbol, start=start)
    df.reset_index(inplace=True)
    
    # Flatten multi-level columns from yfinance
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]

    pl_df = pl.from_pandas(df)
    file_path = RAW_DATA / f"{symbol}.parquet"
    pl_df.write_parquet(file_path)

    print(f"Saved {symbol} data to {file_path}")
    return pl_df
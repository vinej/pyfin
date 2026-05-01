import polars as pl
from src.config.settings import RAW_DATA

def load_data(symbol="AAPL"):
    file_path = RAW_DATA / f"{symbol}.parquet"
    return pl.read_parquet(file_path)
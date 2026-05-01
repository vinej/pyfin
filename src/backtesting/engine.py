from csv import QUOTE_ALL

from src.data.storage import load_data
from src.strategies.sma_cross import run_strategy
import os
from datetime import datetime
import pandas as pd

def run_backtest(symbol="AAPL"):
    df = load_data(symbol)

    close_prices = df["Close"].to_pandas()
    portfolio = run_strategy(close_prices)

    # Get portfolio statistics
    stats = portfolio.stats()
    print(stats)
    
    # Create outputs directory if it doesn't exist
    os.makedirs("outputs", exist_ok=True)
    
    # Export stats to CSV with timestamp and headers (transposed)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"outputs/{symbol}_backtest_stats_{timestamp}.csv"
    
    # Convert stats to DataFrame and transpose (metrics as headers, values in second row)
    stats_df = pd.DataFrame({metric: [value] for metric, value in stats.items()})
    file_exists = os.path.isfile(csv_file)
    stats_df.to_csv(csv_file, mode='a', header=not file_exists, index=False, quoting=QUOTE_ALL)
    print(f"\nBacktest statistics saved to: {csv_file}")
    
    return portfolio
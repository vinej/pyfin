from src.data.storage import load_data
from src.strategies.sma_cross import run_strategy

def run_backtest(symbol="AAPL"):
    df = load_data(symbol)

    close_prices = df["Close"].to_pandas()
    portfolio = run_strategy(close_prices)

    print(portfolio.stats())
    return portfolio
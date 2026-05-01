from src.data.ingest import fetch_data
from src.backtesting.engine import run_backtest
from src.ui.app import run_ui

if __name__ == "__main__":
    fetch_data("AAPL")
    run_backtest("AAPL")

    # Uncomment to launch UI
    # run_ui()
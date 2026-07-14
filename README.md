# PyFin - Quantitative Finance & Backtesting Platform

A Python-based quantitative finance application for developing, backtesting, and analyzing trading strategies. Built with modern data processing and financial analysis libraries.

## Features

- **Data Ingestion**: Download historical financial data from Yahoo Finance
- **Trading Strategies**: Implement and test trading strategies (SMA Crossover included)
- **Backtesting Engine**: Efficient backtesting using VectorBT with comprehensive performance metrics
- **Machine Learning**: ML model integration for predictive analysis
- **Web UI**: Interactive user interface for strategy visualization and analysis
- **Modular Architecture**: Clean separation of concerns for scalability

## Project Structure

```
pyfin/
├── src/
│   ├── main.py                 # Entry point
│   ├── backtesting/
│   │   └── engine.py           # Backtesting engine
│   ├── config/
│   │   └── settings.py         # Configuration and paths
│   ├── data/
│   │   ├── ingest.py           # Data fetching from Yahoo Finance
│   │   └── storage.py          # Data loading from parquet files
│   ├── ml/
│   │   └── model.py            # Machine learning models
│   ├── strategies/
│   │   └── sma_cross.py        # SMA crossover strategy
│   └── ui/
│       └── app.py              # Web UI (PySide6)
├── data/
│   ├── raw/                    # Raw market data
│   └── processed/              # Processed datasets
├── notebooks/                  # Jupyter notebooks for analysis
├── docker/
│   └── Dockerfile              # Docker configuration
├── environment.yml             # Conda environment specification
└── README.md                   # This file
```

## Requirements

- Python 3.11
- Conda (Miniconda or Anaconda)

## Setup Instructions

### 1. Clone/Navigate to the Repository

```bash
cd pyfin
```

### 2. Create and Activate the Conda Environment

```bash
conda env create --file environment.yml
conda activate quant-lab
```

This will install all required dependencies including:
- Data processing: numpy, pandas, polars, pyarrow
- Backtesting: vectorbt
- Machine learning: scikit-learn, pytorch
- Visualization: matplotlib, plotly
- Financial data: yfinance
- UI: PySide6
- Utilities: python-dotenv

### 3. Fetch Market Data

The historical price data is **not included** in the repository — Yahoo Finance's terms don't allow redistributing it, so `data/raw/` is git-ignored (the app creates it on first run via `src/config/settings.py`). Download it yourself with the ingestion helper; each symbol is saved as `data/raw/<SYMBOL>.parquet`.

Fetch a single symbol:

```bash
python -c "from src.data.ingest import fetch_data; fetch_data('AAPL')"
```

Fetch the default set used by the examples (AAPL, SPY, QQQ, IWM, GIB):

```bash
python -c "from src.data.ingest import fetch_data; [fetch_data(s) for s in ['AAPL','SPY','QQQ','IWM','GIB']]"
```

`fetch_data(symbol, start='2020-01-01')` takes an optional start date — change it to pull more or less history. Running `python -m src.main` (below) also fetches AAPL automatically before backtesting.

### 4. Verify Installation

```bash
python -m src.main
```

This will:
- Download AAPL historical data
- Run the SMA crossover backtest
- Display performance statistics

## Usage

### Running the Backtest

```bash
python -m src.main
```

### Launching the Web UI

Uncomment the UI launch in [src/main.py](src/main.py):

```python
if __name__ == "__main__":
    fetch_data("AAPL")
    run_backtest("AAPL")
    run_ui()  # Uncomment this line
```

Then run:
```bash
python -m src.main
```

### Testing a Different Stock

Modify [src/main.py](src/main.py):

```python
symbol = "MSFT"  # Change to any ticker symbol
fetch_data(symbol)
run_backtest(symbol)
```

## Strategy Example: SMA Crossover

The default strategy implements a Simple Moving Average crossover:
- **Fast MA**: 10-period moving average
- **Slow MA**: 50-period moving average
- **Entry Signal**: When fast MA crosses above slow MA
- **Exit Signal**: When fast MA crosses below slow MA
- **Initial Capital**: $10,000

See [src/strategies/sma_cross.py](src/strategies/sma_cross.py) for implementation details.

## Backtest Output

The backtest returns comprehensive statistics including:
- **Total Return**: Overall profit/loss percentage
- **Max Drawdown**: Largest peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted returns
- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Gross profit vs. gross loss
- And more...

## Docker Support

Build and run in a containerized environment:

```bash
docker build -f docker/Dockerfile -t pyfin .
docker run -it pyfin python -m src.main
```

## Development

### Adding a New Strategy

1. Create a new file in `src/strategies/`
2. Implement a function that takes close prices and returns a portfolio
3. Import and use it in `src/backtesting/engine.py`

### Adding ML Models

1. Implement models in `src/ml/model.py`
2. Integrate with the backtesting engine for predictions

## Technologies Used

- **yfinance**: Financial data download
- **vectorbt**: Fast backtesting framework
- **pandas/polars**: Data manipulation
- **scikit-learn**: Machine learning
- **PyTorch**: Deep learning
- **plotly/matplotlib**: Visualization
- **PySide6**: Cross-platform UI

## Troubleshooting

### ModuleNotFoundError: No module named 'polars'

Make sure the conda environment is activated:
```bash
conda activate quant-lab
```

### ColumnNotFoundError: "Close" not found

This is automatically handled in the current version. If encountered, ensure you're using the latest code.

## Future Enhancements

- Real-time trading integration
- Portfolio optimization tools
- Risk management models
- Advanced visualization dashboards
- Historical performance tracking
- Strategy parameter optimization

## License

MIT — see [LICENSE](LICENSE).

## Contact

For questions or issues, please open an issue in the repository.

"""
Portfolio module for managing portfolio definitions and operations.
Handles loading portfolio definitions from CSV files and running backtests on portfolios.
"""

import pandas as pd
import os
from datetime import datetime
import vectorbt as vbt

from src.data.ingest import fetch_data
from src.data.storage import load_data
from src.strategies.sma_cross import run_strategy


def load_portfolio_definition(portfolio_name):
    """
    Load portfolio definition from CSV file.
    
    Args:
        portfolio_name: Name of portfolio (filename without .csv)
    
    Returns:
        DataFrame with columns: Ticker, Quantity, DateBuy, Price
    
    Raises:
        FileNotFoundError: If portfolio CSV file doesn't exist
    """
    portfolio_file = f"data/portfolios/{portfolio_name}.csv"
    
    if not os.path.exists(portfolio_file):
        raise FileNotFoundError(f"Portfolio file not found: {portfolio_file}")
    
    df = pd.read_csv(portfolio_file)
    
    # Validate required columns
    required_cols = ['Ticker', 'Quantity', 'DateBuy', 'Price']
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns in portfolio CSV: {missing_cols}")
    
    return df


def backtest_portfolio(portfolio_name, start_date, end_date, strategy='sma_cross'):
    """
    Run backtest on all tickers in a portfolio.
    
    Args:
        portfolio_name: Name of portfolio (filename without .csv)
        start_date: Start date (datetime object)
        end_date: End date (datetime object)
        strategy: Trading strategy name (default: sma_cross)
    
    Returns:
        Dictionary with portfolio results and individual ticker results
    """
    print(f"\n{'='*60}")
    print(f"PORTFOLIO BACKTEST: {portfolio_name.upper()}")
    print(f"{'='*60}")
    
    # Load portfolio definition
    portfolio_df = load_portfolio_definition(portfolio_name)
    print(f"\nPortfolio Definition:")
    print(portfolio_df)
    
    # Store results for each ticker
    results = {
        'portfolio_name': portfolio_name,
        'start_date': start_date,
        'end_date': end_date,
        'strategy': strategy,
        'tickers': {},
        'combined_portfolio': None
    }
    
    # Collect all portfolios for weighted combination
    all_portfolios = []
    total_capital = 0
    
    # Process each ticker in portfolio
    for idx, row in portfolio_df.iterrows():
        ticker = row['Ticker']
        quantity = float(row['Quantity'])
        
        print(f"\n--- Processing {ticker} (Quantity: {quantity}) ---")
        
        try:
            # Fetch data first
            print(f"Fetching data for {ticker}...")
            fetch_data(ticker)
            
            # Load data
            df = load_data(ticker)
            close_prices = df["Close"].to_pandas()
            
            # Run strategy
            portfolio = run_strategy(close_prices)
            stats = portfolio.stats()
            
            # Calculate initial capital from quantity and entry price
            entry_price = float(row['Price'])
            initial_capital = quantity * entry_price
            total_capital += initial_capital
            
            results['tickers'][ticker] = {
                'quantity': quantity,
                'entry_price': entry_price,
                'initial_capital': initial_capital,
                'portfolio': portfolio,
                'stats': stats
            }
            
            print(f"Return: {stats.get('Total Return [%]', 'N/A')}%")
            
        except Exception as e:
            print(f"Error processing {ticker}: {str(e)}")
            results['tickers'][ticker] = {'error': str(e)}
    
    # Calculate portfolio weight allocation
    print(f"\n{'='*60}")
    print("PORTFOLIO SUMMARY")
    print(f"{'='*60}")
    print(f"Total Initial Capital: ${total_capital:,.2f}")
    print(f"\nWeights:")
    
    for ticker, ticker_data in results['tickers'].items():
        if 'error' not in ticker_data:
            weight = (ticker_data['initial_capital'] / total_capital) * 100
            print(f"  {ticker}: {weight:.2f}% (${ticker_data['initial_capital']:,.2f})")
    
    return results


def get_portfolio_performance(portfolio_name, start_date, end_date):
    """
    Analyze performance metrics for a portfolio.
    
    Args:
        portfolio_name: Name of portfolio (filename without .csv)
        start_date: Start date (datetime object)
        end_date: End date (datetime object)
    
    Returns:
        Dictionary with performance analysis
    """
    print(f"\n{'='*60}")
    print(f"PORTFOLIO PERFORMANCE: {portfolio_name.upper()}")
    print(f"{'='*60}")
    
    # Load portfolio definition
    portfolio_df = load_portfolio_definition(portfolio_name)
    print(f"\nPortfolio Definition:")
    print(portfolio_df)
    
    # Calculate weighted performance
    total_initial = 0
    weighted_returns = 0
    results = {
        'portfolio_name': portfolio_name,
        'start_date': start_date,
        'end_date': end_date,
        'tickers': {}
    }
    
    for idx, row in portfolio_df.iterrows():
        ticker = row['Ticker']
        quantity = float(row['Quantity'])
        entry_price = float(row['Price'])
        initial_capital = quantity * entry_price
        total_initial += initial_capital
        
        try:
            # Fetch data first
            print(f"Fetching data for {ticker}...")
            fetch_data(ticker)
            
            # Load data
            df = load_data(ticker)
            close_prices = df["Close"].to_pandas()
            
            # Run strategy
            portfolio = run_strategy(close_prices)
            stats = portfolio.stats()
            
            total_return_pct = stats.get('Total Return [%]', 0)
            weight = initial_capital / total_initial if total_initial > 0 else 0
            weighted_return = (total_return_pct / 100) * weight
            weighted_returns += weighted_return
            
            results['tickers'][ticker] = {
                'weight': weight * 100,
                'return_pct': total_return_pct,
                'weighted_return_pct': weighted_return * 100,
                'stats': stats
            }
            
            print(f"{ticker}: {total_return_pct:.2f}% return (Weight: {weight*100:.2f}%)")
            
        except Exception as e:
            print(f"Error processing {ticker}: {str(e)}")
            results['tickers'][ticker] = {'error': str(e)}
    
    # Calculate portfolio weighted return
    portfolio_return = weighted_returns * 100
    results['total_return_pct'] = portfolio_return
    results['total_initial_capital'] = total_initial
    
    print(f"\n{'='*60}")
    print(f"Portfolio Weighted Return: {portfolio_return:.2f}%")
    print(f"Total Initial Capital: ${total_initial:,.2f}")
    print(f"{'='*60}\n")
    
    return results

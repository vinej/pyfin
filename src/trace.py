"""
Trace module for visualizing trading signals and execution.
Provides interactive Plotly visualizations of strategy signals and trades.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import vectorbt as vbt
from datetime import datetime
import pandas as pd

from src.data.ingest import fetch_data
from src.data.storage import load_data
from src.strategies.sma_cross import run_strategy


def plot_signals(symbol, close_prices, entries, exits, output_file=None):
    """
    Plot price with buy/sell signals.
    
    Args:
        symbol: Stock ticker symbol
        close_prices: Series of close prices
        entries: Boolean series of entry signals
        exits: Boolean series of exit signals
        output_file: Optional file path to save the plot
    
    Returns:
        plotly Figure object
    """
    fig = go.Figure()
    
    # Add close price
    fig.add_trace(go.Scatter(
        x=close_prices.index,
        y=close_prices.values,
        mode='lines',
        name='Close Price',
        line=dict(color='blue', width=2),
        hovertemplate='<b>%{x}</b><br>Close: $%{y:.2f}<extra></extra>'
    ))
    
    # Add buy signals
    if entries.sum() > 0:
        entry_dates = close_prices.index[entries.values]
        entry_prices = close_prices.values[entries.values]
        fig.add_trace(go.Scatter(
            x=entry_dates,
            y=entry_prices,
            mode='markers',
            name='Buy Signal',
            marker=dict(color='green', size=12, symbol='triangle-up'),
            hovertemplate='<b>BUY</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
        ))
    
    # Add sell signals
    if exits.sum() > 0:
        exit_dates = close_prices.index[exits.values]
        exit_prices = close_prices.values[exits.values]
        fig.add_trace(go.Scatter(
            x=exit_dates,
            y=exit_prices,
            mode='markers',
            name='Sell Signal',
            marker=dict(color='red', size=12, symbol='triangle-down'),
            hovertemplate='<b>SELL</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
        ))
    
    fig.update_layout(
        title=f"{symbol} - Trading Signals Trace",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        hovermode='x unified',
        template='plotly_white',
        height=600,
        xaxis_rangeslider_visible=False,
    )
    
    if output_file:
        fig.write_image(output_file, engine='kaleido', format='png')
        print(f"Chart saved to {output_file}")
    
    return fig


def plot_moving_averages(symbol, close_prices, fast_window=10, slow_window=50, output_file=None):
    """
    Plot price with moving averages.
    
    Args:
        symbol: Stock ticker symbol
        close_prices: Series of close prices
        fast_window: Window for fast moving average
        slow_window: Window for slow moving average
        output_file: Optional file path to save the plot
    
    Returns:
        plotly Figure object
    """
    # Calculate moving averages
    fast_ma = vbt.MA.run(close_prices, window=fast_window)
    slow_ma = vbt.MA.run(close_prices, window=slow_window)
    
    fig = go.Figure()
    
    # Add close price
    fig.add_trace(go.Scatter(
        x=close_prices.index,
        y=close_prices.values,
        mode='lines',
        name='Close Price',
        line=dict(color='blue', width=2),
        hovertemplate='<b>Close</b><br>Date: %{x}<br>Price: $%{y:.2f}<extra></extra>'
    ))
    
    # Add fast MA
    fig.add_trace(go.Scatter(
        x=fast_ma.ma.index,
        y=fast_ma.ma.values,
        mode='lines',
        name=f'Fast MA ({fast_window})',
        line=dict(color='orange', width=1.5, dash='dash'),
        hovertemplate='<b>Fast MA</b><br>Date: %{x}<br>Value: $%{y:.2f}<extra></extra>'
    ))
    
    # Add slow MA
    fig.add_trace(go.Scatter(
        x=slow_ma.ma.index,
        y=slow_ma.ma.values,
        mode='lines',
        name=f'Slow MA ({slow_window})',
        line=dict(color='red', width=1.5, dash='dash'),
        hovertemplate='<b>Slow MA</b><br>Date: %{x}<br>Value: $%{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        title=f"{symbol} - Moving Averages ({fast_window}/{slow_window})",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        hovermode='x unified',
        template='plotly_white',
        height=600,
        xaxis_rangeslider_visible=False,
    )
    
    if output_file:
        fig.write_image(output_file, engine='kaleido', format='png')
        print(f"Chart saved to {output_file}")
    
    return fig


def plot_portfolio_performance(symbol, portfolio, output_file=None):
    """
    Plot portfolio equity curve and drawdown.
    
    Args:
        symbol: Stock ticker symbol
        portfolio: VectorBT portfolio object
        output_file: Optional file path to save the plot
    
    Returns:
        plotly Figure object
    """
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3],
        subplot_titles=("Portfolio Value", "Drawdown")
    )
    
    # Get portfolio value over time
    equity = portfolio.value()
    # Convert to pandas Series if needed
    if hasattr(equity, 'to_pandas'):
        equity = equity.to_pandas()
    
    # Get drawdown over time
    drawdown = portfolio.drawdown()
    if hasattr(drawdown, 'to_pandas'):
        drawdown = drawdown.to_pandas()
    
    # Extract dates
    dates = equity.index if hasattr(equity, 'index') else range(len(equity))
    
    # Add portfolio value
    fig.add_trace(go.Scatter(
        x=dates,
        y=equity.values if hasattr(equity, 'values') else equity,
        mode='lines',
        name='Portfolio Value',
        line=dict(color='green', width=2),
        fill='tozeroy',
        hovertemplate='<b>Portfolio Value</b><br>Date: %{x}<br>Value: $%{y:.2f}<extra></extra>'
    ), row=1, col=1)
    
    # Add drawdown
    fig.add_trace(go.Scatter(
        x=dates,
        y=(drawdown.values if hasattr(drawdown, 'values') else drawdown) * 100,
        mode='lines',
        name='Drawdown',
        line=dict(color='red', width=1.5),
        fill='tozeroy',
        hovertemplate='<b>Drawdown</b><br>Date: %{x}<br>DD: %{y:.2f}%<extra></extra>'
    ), row=2, col=1)
    
    fig.update_yaxes(title_text="Value ($)", row=1, col=1)
    fig.update_yaxes(title_text="Drawdown (%)", row=2, col=1)
    fig.update_xaxes(title_text="Date", row=2, col=1)
    
    fig.update_layout(
        title=f"{symbol} - Portfolio Performance",
        hovermode='x unified',
        template='plotly_white',
        height=700,
        showlegend=True,
    )
    
    if output_file:
        fig.write_image(output_file, engine='kaleido', format='png')
        print(f"Chart saved to {output_file}")
    
    return fig


def plot_combined_portfolio_performance(portfolio_name, portfolio_data, output_file=None):
    """
    Plot combined portfolio performance for all tickers.
    
    Args:
        portfolio_name: Portfolio name
        portfolio_data: Dictionary with ticker data including portfolios and quantities
        output_file: Optional file path to save the plot
    
    Returns:
        plotly Figure object
    """
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3],
        subplot_titles=("Combined Portfolio Value", "Portfolio Drawdown")
    )
    
    # Calculate total initial capital
    total_initial_capital = 0
    ticker_values = {}
    ticker_weights = {}
    
    for ticker, data in portfolio_data.items():
        if 'error' not in data:
            quantity = data['quantity']
            entry_price = data.get('entry_price', 0)
            initial_capital = quantity * entry_price
            total_initial_capital += initial_capital
            ticker_values[ticker] = initial_capital
    
    # Calculate weights
    for ticker, value in ticker_values.items():
        weight = value / total_initial_capital if total_initial_capital > 0 else 0
        ticker_weights[ticker] = weight
    
    # Collect portfolio values for each ticker
    combined_equity = None
    combined_drawdown = None
    
    for ticker, data in portfolio_data.items():
        if 'error' not in data and 'portfolio' in data:
            portfolio = data['portfolio']
            weight = ticker_weights.get(ticker, 0)
            
            # Get equity and drawdown
            equity = portfolio.value()
            drawdown = portfolio.drawdown()
            
            # Convert to pandas if needed
            if hasattr(equity, 'to_pandas'):
                equity = equity.to_pandas()
            if hasattr(drawdown, 'to_pandas'):
                drawdown = drawdown.to_pandas()
            
            # Convert to numpy arrays
            equity_vals = equity.values if hasattr(equity, 'values') else equity
            drawdown_vals = drawdown.values if hasattr(drawdown, 'values') else drawdown
            
            # Apply weight to equity values
            weighted_equity = equity_vals * weight
            
            # Add to combined
            if combined_equity is None:
                combined_equity = weighted_equity
                combined_drawdown = drawdown_vals  # Use first ticker's drawdown as base
            else:
                combined_equity = combined_equity + weighted_equity
    
    if combined_equity is not None:
        dates = list(range(len(combined_equity)))
        
        # Add combined portfolio value
        fig.add_trace(go.Scatter(
            x=dates,
            y=combined_equity,
            mode='lines',
            name='Combined Portfolio',
            line=dict(color='blue', width=2),
            fill='tozeroy',
            hovertemplate='<b>Combined Portfolio Value</b><br>Day: %{x}<br>Value: $%{y:.2f}<extra></extra>'
        ), row=1, col=1)
        
        # Add drawdown
        fig.add_trace(go.Scatter(
            x=dates,
            y=combined_drawdown * 100 if combined_drawdown is not None else [],
            mode='lines',
            name='Drawdown',
            line=dict(color='red', width=1.5),
            fill='tozeroy',
            hovertemplate='<b>Drawdown</b><br>Day: %{x}<br>DD: %{y:.2f}%<extra></extra>'
        ), row=2, col=1)
    
    fig.update_yaxes(title_text="Value ($)", row=1, col=1)
    fig.update_yaxes(title_text="Drawdown (%)", row=2, col=1)
    fig.update_xaxes(title_text="Days", row=2, col=1)
    
    fig.update_layout(
        title=f"{portfolio_name} - Combined Portfolio Performance",
        hovermode='x unified',
        template='plotly_white',
        height=700,
        showlegend=True,
    )
    
    if output_file:
        fig.write_html(output_file)
        print(f"Chart saved to {output_file}")
    
    return fig


def trace_ticker(symbol, start_date, end_date, show_plots=True):
    """
    Trace trading signals for a ticker.
    
    Args:
        symbol: Stock ticker symbol
        start_date: Start date (datetime object)
        end_date: End date (datetime object)
        show_plots: Whether to display plots (default: True)
    
    Returns:
        Dictionary with trace results and figures
    """
    print(f"\n{'='*60}")
    print(f"TRACING {symbol}")
    print(f"{'='*60}")
    print(f"Period: {start_date.date()} to {end_date.date()}")
    
    # Load data
    df = load_data(symbol)
    close_prices = df["Close"].to_pandas()
    
    # Run strategy
    fast_ma = vbt.MA.run(close_prices, window=10)
    slow_ma = vbt.MA.run(close_prices, window=50)
    
    entries = fast_ma.ma_crossed_above(slow_ma)
    exits = fast_ma.ma_crossed_below(slow_ma)
    
    # Create portfolio
    portfolio = vbt.Portfolio.from_signals(
        close_prices,
        entries,
        exits,
        init_cash=10000,
        freq='D'
    )
    
    # Generate plots
    print("\nGenerating visualizations...")
    
    signals_fig = plot_signals(symbol, close_prices, entries, exits, 
                               output_file=f"outputs/{symbol}_signals.png")
    
    ma_fig = plot_moving_averages(symbol, close_prices, 
                                  output_file=f"outputs/{symbol}_moving_averages.png")
    
    perf_fig = plot_portfolio_performance(symbol, portfolio, 
                                          output_file=f"outputs/{symbol}_performance.png")
    
    # Print statistics
    print("\nStrategy Statistics:")
    print(portfolio.stats())
    
    results = {
        'symbol': symbol,
        'start_date': start_date,
        'end_date': end_date,
        'entries': entries.sum(),
        'exits': exits.sum(),
        'portfolio': portfolio,
        'figures': {
            'signals': signals_fig,
            'moving_averages': ma_fig,
            'performance': perf_fig,
        }
    }
    
    if show_plots:
        signals_fig.show()
        ma_fig.show()
        perf_fig.show()
    
    return results


def trace_portfolio(portfolio_name, start_date, end_date, show_plots=True):
    """
    Trace trading signals for all tickers in a portfolio with combined performance chart.
    
    Args:
        portfolio_name: Name of portfolio (filename without .csv)
        start_date: Start date (datetime object)
        end_date: End date (datetime object)
        show_plots: Whether to display plots (default: True)
    
    Returns:
        Dictionary with trace results for all tickers
    """
    from src.portfolio import load_portfolio_definition
    
    print(f"\n{'='*60}")
    print(f"TRACING PORTFOLIO: {portfolio_name.upper()}")
    print(f"{'='*60}")
    print(f"Period: {start_date.date()} to {end_date.date()}")
    
    # Load portfolio definition
    portfolio_df = load_portfolio_definition(portfolio_name)
    print(f"\nPortfolio Definition:")
    print(portfolio_df)
    
    results = {
        'portfolio_name': portfolio_name,
        'start_date': start_date,
        'end_date': end_date,
        'tickers': {}
    }
    
    # Process each ticker in portfolio
    for idx, row in portfolio_df.iterrows():
        ticker = row['Ticker']
        quantity = float(row['Quantity'])
        
        print(f"\n--- Processing {ticker} (Quantity: {quantity}) ---")
        
        try:
            # Fetch data
            print(f"Fetching data for {ticker}...")
            fetch_data(ticker)
            
            # Load data
            df = load_data(ticker)
            close_prices = df["Close"].to_pandas()
            
            # Run strategy
            fast_ma = vbt.MA.run(close_prices, window=10)
            slow_ma = vbt.MA.run(close_prices, window=50)
            
            entries = fast_ma.ma_crossed_above(slow_ma)
            exits = fast_ma.ma_crossed_below(slow_ma)
            
            # Create portfolio
            portfolio = vbt.Portfolio.from_signals(
                close_prices,
                entries,
                exits,
                init_cash=10000,
                freq='D'
            )
            
            # Store results
            entry_price = float(row['Price'])
            results['tickers'][ticker] = {
                'quantity': quantity,
                'entry_price': entry_price,
                'entries': entries.sum(),
                'exits': exits.sum(),
                'portfolio': portfolio,
                'stats': portfolio.stats()
            }
            
            print(f"Trace complete for {ticker}")
            
        except Exception as e:
            print(f"Error tracing {ticker}: {str(e)}")
            results['tickers'][ticker] = {'error': str(e)}
    
    # Generate combined performance chart
    print(f"\nGenerating combined portfolio performance chart...")
    perf_fig = plot_combined_portfolio_performance(
        portfolio_name, 
        results['tickers'],
        output_file=f"outputs/{portfolio_name}_combined_performance.html"
    )
    
    results['combined_figure'] = perf_fig
    
    if show_plots:
        perf_fig.show()
    
    return results

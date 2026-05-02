"""
ETF Strategy Optimizer - One-to-Many Backtesting Framework
Implements one-to-many methodology: start with one strategy, optimize parameters, 
test across multiple ETFs, and expand to portfolio combinations.
"""

import pandas as pd
import numpy as np
import vectorbt as vbt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import itertools

from src.data.ingest import fetch_data
from src.data.storage import load_data

class StrategyOptimizer:
    """One-to-many ETF strategy optimizer using vectorbt."""
    
    def __init__(self, etfs, start_date, end_date, initial_cash=10000):
        """
        Initialize optimizer.
        
        Args:
            etfs: List of ETF tickers
            start_date: Start date (datetime)
            end_date: End date (datetime)
            initial_cash: Initial portfolio cash (default: 10000)
        """
        self.etfs = etfs
        self.start_date = start_date
        self.end_date = end_date
        self.initial_cash = initial_cash
        self.data = {}
        self.results = {}
        
    def fetch_etf_data(self):
        """Fetch data for all ETFs."""
        print(f"\n{'='*60}")
        print("FETCHING ETF DATA")
        print(f"{'='*60}")
        
        for etf in self.etfs:
            print(f"Fetching {etf}...")
            try:
                fetch_data(etf)
                df = load_data(etf)
                self.data[etf] = df["Close"].to_pandas()
                print(f"✓ {etf} loaded successfully")
            except Exception as e:
                print(f"✗ Error loading {etf}: {str(e)}")
        
        return self.data
    
    def sma_strategy(self, close_prices, fast_window=10, slow_window=50):
        """
        SMA crossover strategy.
        
        Args:
            close_prices: Series of close prices
            fast_window: Fast moving average window
            slow_window: Slow moving average window
            
        Returns:
            Tuple of (entries, exits) boolean series
        """
        fast_ma = vbt.MA.run(close_prices, window=fast_window)
        slow_ma = vbt.MA.run(close_prices, window=slow_window)
        
        entries = fast_ma.ma_crossed_above(slow_ma)
        exits = fast_ma.ma_crossed_below(slow_ma)
        
        return entries, exits
    
    def rsi_strategy(self, close_prices, period=14, oversold=30, overbought=70):
        """
        RSI momentum strategy.
        
        Args:
            close_prices: Series of close prices
            period: RSI period
            oversold: Oversold threshold
            overbought: Overbought threshold
            
        Returns:
            Tuple of (entries, exits) boolean series
        """
        rsi = vbt.RSI.run(close_prices, period=period)
        
        entries = rsi.rsi.cross_below(oversold)
        exits = rsi.rsi.cross_above(overbought)
        
        return entries, exits
    
    def bbands_strategy(self, close_prices, window=20, num_std=2):
        """
        Bollinger Bands mean reversion strategy.
        
        Args:
            close_prices: Series of close prices
            window: BB window
            num_std: Number of standard deviations
            
        Returns:
            Tuple of (entries, exits) boolean series
        """
        bb = vbt.BBANDS.run(close_prices, window=window, num_std=num_std)
        
        # Entry when price touches lower band
        entries = close_prices <= bb.lower.values
        # Exit when price touches upper band
        exits = close_prices >= bb.upper.values
        
        return entries, exits
    
    def optimize_strategy_single_etf(self, etf, strategy_name='sma_cross', param_grid=None):
        """
        Optimize single strategy across parameter grid for one ETF.
        
        Args:
            etf: ETF ticker
            strategy_name: Strategy name ('sma_cross', 'rsi', 'bbands')
            param_grid: Dictionary of parameters to optimize
            
        Returns:
            DataFrame with optimization results
        """
        if etf not in self.data:
            raise ValueError(f"Data not loaded for {etf}")
        
        close_prices = self.data[etf]
        
        # Default parameter grids
        if param_grid is None:
            if strategy_name == 'sma_cross':
                param_grid = {
                    'fast_window': [5, 10, 20],
                    'slow_window': [30, 50, 100]
                }
            elif strategy_name == 'rsi':
                param_grid = {
                    'period': [10, 14, 21],
                    'oversold': [20, 30, 40],
                    'overbought': [60, 70, 80]
                }
            elif strategy_name == 'bbands':
                param_grid = {
                    'window': [15, 20, 25],
                    'num_std': [1.5, 2.0, 2.5]
                }
        
        results = []
        total_combinations = np.prod([len(v) for v in param_grid.values()])
        print(f"\nOptimizing {strategy_name} for {etf} ({total_combinations} combinations)...")
        
        # Generate all parameter combinations
        param_names = list(param_grid.keys())
        param_values = list(param_grid.values())
        
        for i, combination in enumerate(itertools.product(*param_values)):
            params = dict(zip(param_names, combination))
            
            try:
                # Run strategy
                if strategy_name == 'sma_cross':
                    entries, exits = self.sma_strategy(close_prices, **params)
                elif strategy_name == 'rsi':
                    entries, exits = self.rsi_strategy(close_prices, **params)
                elif strategy_name == 'bbands':
                    entries, exits = self.bbands_strategy(close_prices, **params)
                else:
                    raise ValueError(f"Unknown strategy: {strategy_name}")
                
                # Backtest
                portfolio = vbt.Portfolio.from_signals(
                    close_prices,
                    entries,
                    exits,
                    init_cash=self.initial_cash,
                    freq='D'
                )
                
                stats = portfolio.stats()
                
                # Store results
                result = {
                    'etf': etf,
                    'strategy': strategy_name,
                    **params,
                    'total_return': stats.get('Total Return [%]', 0),
                    'sharpe_ratio': stats.get('Sharpe Ratio', 0),
                    'max_drawdown': stats.get('Max Drawdown [%]', 0),
                    'win_rate': stats.get('Win Rate [%]', 0),
                    'profit_factor': stats.get('Profit Factor', 0),
                }
                results.append(result)
                
                if (i + 1) % 10 == 0 or i == total_combinations - 1:
                    print(f"  Progress: {i+1}/{total_combinations}")
                    
            except Exception as e:
                print(f"  Error with params {params}: {str(e)}")
        
        results_df = pd.DataFrame(results)
        return results_df
    
    def optimize_one_to_many(self, strategy_name='sma_cross', param_grid=None):
        """
        One-to-many optimization: test strategy across all ETFs with parameter grid.
        
        Args:
            strategy_name: Strategy to optimize
            param_grid: Parameter grid
            
        Returns:
            Dictionary with optimization results for each ETF
        """
        print(f"\n{'='*60}")
        print(f"ONE-TO-MANY OPTIMIZATION: {strategy_name.upper()}")
        print(f"{'='*60}")
        print(f"Testing across {len(self.etfs)} ETFs")
        
        all_results = {}
        
        for etf in self.etfs:
            if etf in self.data:
                results_df = self.optimize_strategy_single_etf(etf, strategy_name, param_grid)
                all_results[etf] = results_df
                
                # Print top 5 parameter sets
                top_results = results_df.nlargest(5, 'sharpe_ratio')
                print(f"\nTop 5 parameter sets for {etf} (by Sharpe Ratio):")
                print(top_results[['total_return', 'sharpe_ratio', 'max_drawdown', 'profit_factor']])
        
        return all_results
    
    def rank_etf_performance(self, results_dict):
        """
        Rank ETFs by best strategy performance.
        
        Args:
            results_dict: Dictionary of optimization results
            
        Returns:
            DataFrame with rankings
        """
        rankings = []
        
        for etf, results_df in results_dict.items():
            best = results_df.loc[results_df['sharpe_ratio'].idxmax()]
            rankings.append({
                'etf': etf,
                'best_return': best['total_return'],
                'best_sharpe': best['sharpe_ratio'],
                'best_drawdown': best['max_drawdown'],
                'best_profit_factor': best['profit_factor']
            })
        
        rankings_df = pd.DataFrame(rankings).sort_values('best_sharpe', ascending=False)
        
        print(f"\n{'='*60}")
        print("ETF PERFORMANCE RANKING")
        print(f"{'='*60}")
        print(rankings_df)
        
        return rankings_df
    
    def multi_etf_portfolio_backtest(self, strategy_name='sma_cross', weights=None):
        """
        Backtest portfolio combining multiple ETFs.
        
        Args:
            strategy_name: Strategy to use
            weights: Dictionary of ETF weights (auto-calculated if None)
            
        Returns:
            Portfolio object
        """
        print(f"\n{'='*60}")
        print("MULTI-ETF PORTFOLIO BACKTEST")
        print(f"{'='*60}")
        
        # Auto-weight if not provided
        if weights is None:
            weights = {etf: 1/len(self.etfs) for etf in self.etfs}
        
        print(f"Weights: {weights}")
        
        # Create combined data with weights
        combined_signals = None
        combined_prices = None
        
        for etf in self.etfs:
            if etf not in self.data:
                continue
            
            close_prices = self.data[etf]
            
            # Run strategy
            if strategy_name == 'sma_cross':
                entries, exits = self.sma_strategy(close_prices)
            elif strategy_name == 'rsi':
                entries, exits = self.rsi_strategy(close_prices)
            elif strategy_name == 'bbands':
                entries, exits = self.bbands_strategy(close_prices)
            
            weight = weights.get(etf, 0)
            
            if combined_prices is None:
                combined_prices = close_prices * weight
                combined_signals = entries.astype(float) * weight
            else:
                combined_prices = combined_prices + (close_prices * weight)
                combined_signals = combined_signals + (entries.astype(float) * weight)
        
        # Backtest combined portfolio
        combined_entries = combined_signals > 0
        combined_exits = ~combined_entries
        
        portfolio = vbt.Portfolio.from_signals(
            combined_prices,
            combined_entries,
            combined_exits,
            init_cash=self.initial_cash * len(self.etfs),
            freq='D'
        )
        
        print("\nCombined Portfolio Stats:")
        print(portfolio.stats())
        
        return portfolio
    
    def plot_optimization_results(self, results_dict, output_file=None):
        """
        Plot optimization results across ETFs.
        
        Args:
            results_dict: Dictionary of optimization results
            output_file: Optional file path to save
            
        Returns:
            Plotly figure
        """
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Total Return vs Sharpe Ratio", "Max Drawdown Distribution",
                          "Profit Factor Distribution", "Return by ETF")
        )
        
        for etf, results_df in results_dict.items():
            # Return vs Sharpe
            fig.add_trace(go.Scatter(
                x=results_df['sharpe_ratio'],
                y=results_df['total_return'],
                mode='markers',
                name=etf,
                marker=dict(size=8),
                text=[f"{etf}" for _ in range(len(results_df))],
            ), row=1, col=1)
            
            # Drawdown distribution
            fig.add_trace(go.Box(
                y=results_df['max_drawdown'],
                name=etf,
                boxmean=True,
                showlegend=False
            ), row=1, col=2)
            
            # Profit factor distribution
            fig.add_trace(go.Histogram(
                x=results_df['profit_factor'],
                name=etf,
                opacity=0.7,
                showlegend=False
            ), row=2, col=1)
            
            # Return by ETF
            fig.add_trace(go.Box(
                y=results_df['total_return'],
                name=etf,
                boxmean=True,
                showlegend=False
            ), row=2, col=2)
        
        fig.update_xaxes(title_text="Sharpe Ratio", row=1, col=1)
        fig.update_yaxes(title_text="Total Return (%)", row=1, col=1)
        fig.update_yaxes(title_text="Max Drawdown (%)", row=1, col=2)
        fig.update_xaxes(title_text="Profit Factor", row=2, col=1)
        fig.update_yaxes(title_text="Total Return (%)", row=2, col=2)
        
        fig.update_layout(
            title="Strategy Optimization Results - One-to-Many",
            height=800,
            width=1200,
            hovermode='closest'
        )
        
        if output_file:
            fig.write_html(output_file)
            print(f"Chart saved to {output_file}")
        
        fig.show()
        return fig


def run_etf_optimization_example():
    """Example: Optimize SMA strategy across multiple ETFs."""
    from datetime import datetime, timedelta
    
    # ETFs to test
    etfs = ['SPY', 'QQQ', 'IWM']  # S&P500, Nasdaq, Russell2000
    
    # Date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365*2)  # 2 years
    
    # Initialize optimizer
    optimizer = StrategyOptimizer(etfs, start_date, end_date, initial_cash=10000)
    
    # Step 1: Fetch data
    optimizer.fetch_etf_data()
    
    # Step 2: One-to-many optimization
    sma_results = optimizer.optimize_one_to_many('sma_cross')
    
    # Step 3: Rank ETFs
    rankings = optimizer.rank_etf_performance(sma_results)
    
    # Step 4: Multi-ETF portfolio backtest
    portfolio = optimizer.multi_etf_portfolio_backtest('sma_cross')
    
    # Step 5: Visualization
    optimizer.plot_optimization_results(sma_results, 
                                       output_file='outputs/etf_optimization_results.html')
    
    return optimizer, sma_results, rankings, portfolio

run_etf_optimization_example()


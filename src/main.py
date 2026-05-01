import argparse
import sys
from datetime import datetime

from src.data.ingest import fetch_data
from src.backtesting.engine import run_backtest
from src.ui.app import run_ui
from src.trace import trace_ticker, trace_portfolio
from src.portfolio import backtest_portfolio, get_portfolio_performance


def parse_date(date_string):
    """Parse date string in format YYYY-MM-DD."""
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid date format: {date_string}. Use YYYY-MM-DD")


def cmd_backtest(args):
    """Handle backtest command."""
    print(f"\n{'='*60}")
    print("BACKTEST COMMAND")
    print(f"{'='*60}")
    
    if args.ticker:
        print(f"Ticker: {args.ticker}")
        fetch_data(args.ticker)
        portfolio = run_backtest(args.ticker)
    elif args.portfolio:
        print(f"Portfolio: {args.portfolio}")
        results = backtest_portfolio(args.portfolio, args.startdate, args.enddate, args.strategy)
        return results
    
    print(f"Start Date: {args.startdate}")
    print(f"End Date: {args.enddate}")
    print(f"Strategy: {args.strategy}")
    
    if portfolio:
        print("\nBacktest Results:")
        print(portfolio.stats())
    
    return portfolio


def cmd_trace(args):
    """Handle trace command to trace trades and signals."""
    print(f"\n{'='*60}")
    print("TRACE COMMAND")
    print(f"{'='*60}")
    
    if args.ticker:
        print(f"Ticker: {args.ticker}")
        print(f"Start Date: {args.startdate}")
        print(f"End Date: {args.enddate}")
        # Call trace functionality
        results = trace_ticker(args.ticker, args.startdate, args.enddate, show_plots=True)
    elif args.portfolio:
        print(f"Portfolio: {args.portfolio}")
        print(f"Start Date: {args.startdate}")
        print(f"End Date: {args.enddate}")
        # Call portfolio trace functionality
        results = trace_portfolio(args.portfolio, args.startdate, args.enddate, show_plots=True)
    
    return results


def cmd_performance(args):
    """Handle performance command to analyze performance metrics."""
    print(f"\n{'='*60}")
    print("PERFORMANCE COMMAND")
    print(f"{'='*60}")
    
    if args.ticker:
        print(f"Ticker: {args.ticker}")
        fetch_data(args.ticker)
        portfolio = run_backtest(args.ticker)
    elif args.portfolio:
        print(f"Portfolio: {args.portfolio}")
        results = get_portfolio_performance(args.portfolio, args.startdate, args.enddate)
        return results
    
    print(f"Start Date: {args.startdate}")
    print(f"End Date: {args.enddate}")
    
    if portfolio:
        print("\nPerformance Metrics:")
        stats = portfolio.stats()
        print(stats)
    
    return portfolio


def create_parser():
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        description="PyFin: Financial Backtesting and Analysis Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.main backtest --ticker AAPL --startdate 2023-01-01 --enddate 2024-01-01 --strategy sma_cross
  python -m src.main backtest --portfolio myportfolio --startdate 2023-01-01 --enddate 2024-01-01 --strategy sma_cross
  python -m src.main trace --ticker AAPL --startdate 2023-01-01 --enddate 2024-01-01
  python -m src.main trace --portfolio myportfolio --startdate 2023-01-01 --enddate 2024-01-01
  python -m src.main performance --ticker AAPL --startdate 2023-01-01 --enddate 2024-01-01
  python -m src.main performance --portfolio myportfolio --startdate 2023-01-01 --enddate 2024-01-01
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Backtest command
    backtest_parser = subparsers.add_parser('backtest', help='Run backtest on ticker or portfolio')
    backtest_group = backtest_parser.add_mutually_exclusive_group(required=True)
    backtest_group.add_argument('--ticker', type=str, help='Stock ticker symbol (e.g., AAPL)')
    backtest_group.add_argument('--portfolio', type=str, help='Portfolio name')
    backtest_parser.add_argument('--startdate', type=parse_date, required=True, help='Start date (YYYY-MM-DD)')
    backtest_parser.add_argument('--enddate', type=parse_date, required=True, help='End date (YYYY-MM-DD)')
    backtest_parser.add_argument('--strategy', type=str, default='sma_cross', help='Strategy name (default: sma_cross)')
    backtest_parser.set_defaults(func=cmd_backtest)
    
    # Trace command
    trace_parser = subparsers.add_parser('trace', help='Trace trading signals for a ticker or portfolio')
    trace_group = trace_parser.add_mutually_exclusive_group(required=True)
    trace_group.add_argument('--ticker', type=str, help='Stock ticker symbol (e.g., AAPL)')
    trace_group.add_argument('--portfolio', type=str, help='Portfolio name')
    trace_parser.add_argument('--startdate', type=parse_date, required=True, help='Start date (YYYY-MM-DD)')
    trace_parser.add_argument('--enddate', type=parse_date, required=True, help='End date (YYYY-MM-DD)')
    trace_parser.set_defaults(func=cmd_trace)
    
    # Performance command
    performance_parser = subparsers.add_parser('performance', help='Analyze performance metrics')
    perf_group = performance_parser.add_mutually_exclusive_group(required=True)
    perf_group.add_argument('--ticker', type=str, help='Stock ticker symbol (e.g., AAPL)')
    perf_group.add_argument('--portfolio', type=str, help='Portfolio name')
    performance_parser.add_argument('--startdate', type=parse_date, required=True, help='Start date (YYYY-MM-DD)')
    performance_parser.add_argument('--enddate', type=parse_date, required=True, help='End date (YYYY-MM-DD)')
    performance_parser.set_defaults(func=cmd_performance)
    
    return parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(0)
    
    try:
        args.func(args)
    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        sys.exit(1)
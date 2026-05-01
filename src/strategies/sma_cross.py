import vectorbt as vbt

def run_strategy(close_prices):
    fast_ma = vbt.MA.run(close_prices, window=10)
    slow_ma = vbt.MA.run(close_prices, window=50)

    entries = fast_ma.ma_crossed_above(slow_ma)
    exits = fast_ma.ma_crossed_below(slow_ma)

    portfolio = vbt.Portfolio.from_signals(
        close_prices,
        entries,
        exits,
        init_cash=10000
    )

    return portfolio
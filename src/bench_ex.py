import json
import pandas as pd
import vectorbt as vbt

class PortfolioLoader:

    def __init__(self, config_path):
        self.config = json.load(open(config_path))

    def load_data(self):
        tickers = self.config["universe"]["tickers"]
        start = self.config["universe"]["date_range"]["start"]
        end = self.config["universe"]["date_range"]["end"]  
        df =  vbt.YFData.download(tickers, start=start, end=end, interval=self.config["universe"]["frequency"])
        return df.get("Close").ffill()

    def build_strategies(self, data):
        entries = pd.DataFrame(False, index=data.index, columns=data.columns)
        exits = pd.DataFrame(False, index=data.index, columns=data.columns)

        for strat in self.config["strategies"]:
            if strat["type"] == "signal":
                e, x = self._build_signal_strategy(data, strat)
                entries.loc[:, e.columns] |= e
                exits.loc[:, x.columns] |= x

            elif strat["type"] == "allocation":
                # buy & hold → entry at first bar
                cols = strat["applies_to"]
                entries.loc[data.index[0], cols] = True

        return entries, exits

    def _build_signal_strategy(self, data, strat):
        cols = strat["applies_to"]
        sub = data[cols]

        if strat["name"] == "sma_cross":
            fast = sub.rolling(strat["params"]["fast"]).mean()
            slow = sub.rolling(strat["params"]["slow"]).mean()

            entries = fast > slow
            exits = fast < slow

            return entries, exits

        raise ValueError(f"Unknown strategy {strat['name']}")

    def build_weights(self, data):
        weights_cfg = self.config["allocation"]["weights"]
        weights = pd.DataFrame(0, index=data.index, columns=data.columns)

        for t, w in weights_cfg.items():
            weights[t] = w

        return weights

    def apply_rebalancing(self, weights, data):
        rebalance_cfg = self.config["allocation"]["rebalance"]

        if not rebalance_cfg["enabled"]:
            return weights

        freq = rebalance_cfg["frequency"]

        if freq == "monthly":
            mask = data.index.to_series().dt.is_month_start
            weights = weights.where(mask)

        return weights

    def build_portfolio(self):
        data = self.load_data()

        entries, exits = self.build_strategies(data)
        weights = self.build_weights(data)
        weights = self.apply_rebalancing(weights, data)

        pf = vbt.Portfolio.from_signals(
            data,
            entries,
            exits,
            init_cash=self.config["cash"]["initial_capital"],
            fees=self.config["execution"]["fees"],
            slippage=self.config["execution"]["slippage"]
        )

        return pf
    

p = PortfolioLoader("C:\\learnai\\pyfin\\data\\portfolios\\test01.json")

pf = p.build_portfolio()

print(pf.stats())
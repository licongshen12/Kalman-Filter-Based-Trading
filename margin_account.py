class MarginAccount:
    def __init__(self, initial_cash=100_000, leverage=10, maintenance_margin_ratio=0.25):
        self.cash = initial_cash  # Starting capital
        self.positions = {
            "perp": {"quantity": 0.0, "entry_price": 0.0},
            "future": {"quantity": 0.0, "entry_price": 0.0},
        }
        self.leverage = leverage
        self.maintenance_margin_ratio = maintenance_margin_ratio
        self.liquidated = False
        self.trade_log = []

    def update_position(self, market_price_perp, market_price_future):
        # Compute unrealized PnL
        perp_pnl = self.positions["perp"]["quantity"] * (market_price_perp - self.positions["perp"]["entry_price"])
        future_pnl = self.positions["future"]["quantity"] * (market_price_future - self.positions["future"]["entry_price"])
        return perp_pnl + future_pnl

    def margin_required(self):
        # 10% initial margin required per position for both perp and futures
        perp_margin = abs(self.positions["perp"]["quantity"] * self.positions["perp"]["entry_price"]) / self.leverage
        future_margin = abs(self.positions["future"]["quantity"] * self.positions["future"]["entry_price"]) / self.leverage
        return perp_margin + future_margin

    def margin_ratio(self, market_price_perp, market_price_future):
        equity = self.cash + self.update_position(market_price_perp, market_price_future)
        margin_required = self.margin_required()
        if margin_required == 0:
            return float("inf")  # No margin needed if no positions
        return equity / margin_required

    def check_liquidation(self, market_price_perp, market_price_future):
        if self.margin_ratio(market_price_perp, market_price_future) < self.maintenance_margin_ratio:
            self.liquidated = True
            return True
        return False

# Create and display a margin account object
account = MarginAccount()
account.__dict__

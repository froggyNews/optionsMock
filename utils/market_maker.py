import streamlit as st

from .live_trader import LiveTrader


class MarketMaker(LiveTrader):
    """Live trader subclass implementing market maker logic."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inventory = st.session_state.get("maker_inventory", 0)
        self.quote = None

    def post_quote(self, bid: float, ask: float, qty: int) -> None:
        """Post a bid/ask quote to the market."""
        self.quote = {"bid": bid, "ask": ask, "qty": qty}
        st.session_state.maker_quote = self.quote

    def execute_trade(self, side: str, qty: int, price: float) -> None:
        """Handle a trade fill against our quote."""
        if side.lower() == "buy":
            self.inventory -= qty
        elif side.lower() == "sell":
            self.inventory += qty
        st.session_state.maker_inventory = self.inventory
        quote_price = self.quote["ask"] if side.lower() == "buy" else self.quote["bid"]
        pnl = (price - quote_price) * qty
        st.session_state.setdefault("maker_pnl", 0)
        st.session_state["maker_pnl"] += pnl

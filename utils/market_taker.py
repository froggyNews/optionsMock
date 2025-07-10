import streamlit as st

from .live_trader import LiveTrader


class MarketTaker(LiveTrader):
    """Simple live trader subclass for taker style workflows."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inventory = st.session_state.get("taker_inventory", 0)

    def execute_trade(self, side: str, qty: int) -> None:
        """Execute an immediate trade and update inventory."""
        if side.lower() == "buy":
            self.inventory += qty
        elif side.lower() == "sell":
            self.inventory -= qty
        st.session_state.taker_inventory = self.inventory

    def post_quote(self, *args, **kwargs):  # pragma: no cover - placeholder
        st.info("Market takers do not post quotes.")

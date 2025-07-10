import numpy as np
import streamlit as st

from .live_trader import LiveTrader
from .ui_config import maker_quote_form


class MarketMaker(LiveTrader):
    """Live trader subclass implementing market maker logic."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.inventory = st.session_state.get("maker_inventory", 0)
        self.quote = None
        self.pnl_history = st.session_state.get("maker_pnl_history", [])

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
        pnl = (price - self.quote[side.lower() == "buy" and "ask" or "bid"]) * qty
        st.session_state.setdefault("maker_pnl", 0)
        st.session_state["maker_pnl"] += pnl

    # --- Simple Quoting Simulation Interface ---
    def render(self) -> None:
        """Render quote posting and simulated fill workflow."""
        st.subheader("Live Quoting")

        quote = maker_quote_form()
        if quote:
            self.post_quote(**quote)
            st.success("Quote posted")

        if self.quote and st.button("Simulate Fill"):
            side = np.random.choice(["buy", "sell"])
            price = self.quote["ask"] if side == "buy" else self.quote["bid"]
            self.execute_trade(side, self.quote["qty"], price)
            st.success(f"Filled {side} {self.quote['qty']} @ {price:.2f}")
            st.write("Inventory:", self.inventory)

        current_pnl = st.session_state.get("maker_pnl", 0)
        if self.pnl_history and self.pnl_history[-1] == current_pnl:
            pass
        else:
            self.pnl_history.append(current_pnl)
            st.session_state.maker_pnl_history = self.pnl_history

        if self.pnl_history:
            st.line_chart(self.pnl_history)

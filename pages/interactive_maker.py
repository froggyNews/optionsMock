import numpy as np
import streamlit as st

from utils import greeks, option_pricing as op, scenario_generator
from utils.market_maker import MarketMaker
from utils.ui_config import difficulty_selector, maker_quote_form

st.set_page_config(page_title="Market Maker")

st.title("Market Maker Practice")

difficulty_selector()

if "scenario" not in st.session_state:
    st.session_state["scenario"] = scenario_generator.generate_scenario()

sc = st.session_state["scenario"]

call_delta = greeks.call_delta(sc["S"], sc["K"], sc["r"], sc["T"], sc["sigma"])
put_delta = greeks.put_delta(sc["S"], sc["K"], sc["r"], sc["T"], sc["sigma"])
call_theo = op.call_price(sc["S"], sc["K"], sc["r"], sc["T"], sc["sigma"])
put_theo = op.put_price(sc["S"], sc["K"], sc["r"], sc["T"], sc["sigma"])

maker = MarketMaker(sc, call_delta, put_delta, call_theo, put_theo)

st.write(sc)
quote = maker_quote_form()
if quote:
    maker.post_quote(**quote)
    st.success("Quote posted")

if st.button("Simulate Fill") and maker.quote:
    side = np.random.choice(["buy", "sell"])
    price = maker.quote["ask"] if side == "buy" else maker.quote["bid"]
    maker.execute_trade(side, maker.quote["qty"], price)
    st.success(f"Filled {side} {maker.quote['qty']} @ {price:.2f}")
    st.write("Inventory:", maker.inventory)

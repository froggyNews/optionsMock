import streamlit as st

from utils import greeks, option_pricing as op, scenario_generator
from utils.market_taker import MarketTaker
from utils.ui_config import difficulty_selector, taker_trade_form

st.set_page_config(page_title="Market Taker")

st.title("Market Taker Practice")

difficulty_selector()

if "scenario" not in st.session_state:
    st.session_state["scenario"] = scenario_generator.generate_scenario()

sc = st.session_state["scenario"]

call_delta = greeks.call_delta(sc["S"], sc["K"], sc["r"], sc["T"], sc["sigma"])
put_delta = greeks.put_delta(sc["S"], sc["K"], sc["r"], sc["T"], sc["sigma"])
call_theo = op.call_price(sc["S"], sc["K"], sc["r"], sc["T"], sc["sigma"])
put_theo = op.put_price(sc["S"], sc["K"], sc["r"], sc["T"], sc["sigma"])

trader = MarketTaker(sc, call_delta, put_delta, call_theo, put_theo)

st.write(sc)
trade = taker_trade_form()
if trade:
    trader.execute_trade(trade["side"], trade["qty"])
    st.success(f"Inventory now {trader.inventory}")

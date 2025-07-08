import streamlit as st
import pandas as pd
from utils import trade_simulation as ts
from utils import scenario_generator
from utils import greeks

st.header("Interactive Arbitrage Trainer")

if st.button("Generate Scenario") or "scenario" not in st.session_state:
    st.session_state.scenario = scenario_generator.generate_scenario()

sc = st.session_state.scenario

st.write(
    f"S={sc['S']:.2f}, K={sc['K']:.2f}, T={sc['T']:.2f}yr, r={sc['r']:.4f}, σ={sc['sigma']:.2f}"
)
st.write(
    f"Call Market={sc['C_mkt']:.2f} (Theo {sc['C_theo']:.2f}),  "
    f"Put Market={sc['P_mkt']:.2f} (Theo {sc['P_theo']:.2f})"
)

col1, col2 = st.columns(2)
with col1:
    call_action = st.selectbox("Call", ["None", "Buy", "Sell"])
    put_action = st.selectbox("Put", ["None", "Buy", "Sell"])
with col2:
    stock_action = st.selectbox("Stock", ["None", "Long", "Short"])
    cash_action = st.selectbox("Cash", ["None", "Borrow", "Lend"])

if st.button("Simulate Trade"):
    trade = ts.trade_from_choices(call_action, put_action, stock_action, cash_action)
    cf0, pnls = ts.simulate_trade(sc, trade)
    st.write(f"Initial cash flow: {cf0:.2f}")
    df = pd.DataFrame({"Price": list(pnls.keys()), "PnL": list(pnls.values())})
    st.table(df)
    st.line_chart(df.set_index("Price"))

    correct_trade = ts.TRADE_MAP[sc["arb"]]
    correct = trade == correct_trade
    st.write("Trade evaluation:", "Correct" if correct else f"Incorrect ({sc['arb']})")

    pos_greeks = greeks.net_position_greeks(trade, sc['S'], sc['K'], sc['r'], sc['T'], sc['sigma'])
    sig = {k: v for k, v in pos_greeks.items() if abs(v) > 0.2}
    user_sel = st.multiselect("Which Greeks matter?", greeks.GREEK_KEYS)
    if st.button("Check Greeks"):
        missed = [g for g in sig if g not in user_sel]
        extra = [g for g in user_sel if g not in sig]
        if not missed and not extra:
            st.success("Correct Greeks identified")
        else:
            if missed:
                st.write("Missed:", ", ".join(missed))
            if extra:
                st.write("Not significant:", ", ".join(extra))
        for g, val in pos_greeks.items():
            st.write(f"{g.capitalize()}: {val:.2f}")

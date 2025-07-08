import streamlit as st
from utils import parity
from utils import trade_simulation as ts

st.header("Mock Trade Simulation")

difficulty = st.session_state.get("difficulty", "Standard")

if st.button("Generate Scenario") or "sim_params" not in st.session_state:
    st.session_state.sim_params = parity.generate_parameters(difficulty=difficulty)
params = st.session_state.sim_params

eq = (
    rf"S = {params['S']:.2f},\; K = {params['K']:.2f},\; C = {params['C']:.2f},\;"
    rf"\; P = {params['P']:.2f},\; r = {params['r']:.3f},\; T = {params['T']:.2f}"
)
st.latex(eq)

col1, col2 = st.columns(2)
with col1:
    call_choice = st.selectbox("Call", ["Buy", "Sell", "None"])
    put_choice = st.selectbox("Put", ["Buy", "Sell", "None"])
with col2:
    stock_choice = st.selectbox("Stock", ["Long", "Short", "None"])
    pvk_choice = st.selectbox("PV(K)", ["Borrow", "Lend", "None"])

if st.button("Run Simulation"):
    trade = ts.trade_from_choices(call_choice, put_choice, stock_choice, pvk_choice)
    cf0, pnls = ts.simulate_trade(params, trade)
    violated, diff = parity.parity_violation(params)
    correct_trade = parity.arbitrage_strategy(diff)
    correct = trade == ts.TRADE_MAP[correct_trade]
    st.write("Net cash flow at inception:", f"{cf0:.2f}")
    st.write("P&L Scenarios:")
    for price, pnl in pnls.items():
        st.write(f"S={price}: {pnl:.2f}")
    st.write("Correct" if correct else f"Incorrect, expected: {correct_trade}")
    st.write("Explanation:")
    st.latex(r"C - P \stackrel{?}{=} S - K e^{-rT}")
    st.write(f"Difference: {diff:.2f}")
    st.write("User trade:", trade)
    st.write("Required trade:", ts.TRADE_MAP[correct_trade])


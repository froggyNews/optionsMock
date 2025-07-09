import streamlit as st
import numpy as np
from utils import parity

st.header("Put-Call Parity Practice")

difficulty = st.session_state.get("difficulty", "Standard")

if st.button("Generate New Parameters") or "pcp_params" not in st.session_state:
    st.session_state.pcp_params = parity.generate_parameters(difficulty=difficulty)
params = st.session_state.pcp_params

param_eq = (
    rf"S = {params['S']:.2f},\; K = {params['K']:.2f},\; C = {params['C']:.2f},\;"
    rf"\; P = {params['P']:.2f},\; r = {params['r']:.3f},\; T = {params['T']:.2f}"
)
st.latex(param_eq)

df = np.exp(-params["r"] * params["T"])
st.latex(rf"e^{{-r T}} = {df:.3f}")

if "show_formula" not in st.session_state:
    st.session_state.show_formula = False
if st.session_state.show_formula:
    if st.button("Hide Parity Formula"):
        st.session_state.show_formula = False
else:
    if st.button("Show Parity Formula"):
        st.session_state.show_formula = True
if st.session_state.show_formula:
    st.latex(r"C - P = S - K e^{-r T}")

violation_user = st.radio("Is parity violated?", ("Yes", "No"))
trade_user = st.radio(
    "Arbitrage Trade",
    (
        "Buy call, sell put, buy stock, borrow PV(K)",
        "Sell call, buy put, short stock, lend PV(K)",
        "No trade",
    ),
)

if st.button("Check Answer"):
    violated, diff = parity.parity_violation(params)
    arb = parity.arbitrage_strategy(diff)
    correct = (
        (violated and violation_user == "Yes")
        or (not violated and violation_user == "No")
    ) and trade_user == arb
    st.write("Correct" if correct else "Incorrect")
    st.latex(r"C - P = S - K e^{-r T}")
    st.latex(rf"C - P - (S - K e^{{-r T}}) = {diff:.2f}")
    parity.payoff_diagram(params, diff)


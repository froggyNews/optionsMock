import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from option_pricing import call_price, put_price
from options_chain import generate_chain
import parity
import delta_hedging as dh
import quiz
import trade_simulation as ts

def setup_page_config():
    st.set_page_config(
        page_title="Options Practice App",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def initialize_session_state():
    if "pcp_params" not in st.session_state:
        st.session_state.pcp_params = None
    if "dh_state" not in st.session_state:
        st.session_state.dh_state = None
    if "dh_history" not in st.session_state:
        st.session_state.dh_history = []
    if "quiz" not in st.session_state:
        st.session_state.quiz = None
    if "show_answer" not in st.session_state:
        st.session_state.show_answer = False

def options_chain_page():
    st.header("Options Chain Builder")
    spot = st.number_input("Spot Price", value=100.0)
    r = st.number_input("Risk Free Rate", value=0.01)
    vol = st.number_input("Implied Volatility", value=0.2)
    width = st.number_input("Strike Width", value=5.0)
    strikes = np.arange(spot - 2 * width, spot + 2 * width + width, width)
    expiries_months = st.multiselect("Expiry Months", options=[1, 2, 3], default=[1, 2, 3])
    expiries = [m / 12 for m in expiries_months]

    if expiries:
        df_chain = generate_chain(spot, r, expiries, strikes, vol)
        st.dataframe(df_chain)

        if "prompt" not in st.session_state:
            st.session_state.prompt = None

        if st.button("Random Prompt"):
            row = df_chain.sample(1).iloc[0]
            mkt_price = row["Call Price"] * (1 + np.random.uniform(-0.2, 0.2))
            st.session_state.prompt = {
                "row": row.to_dict(),
                "mkt_price": float(mkt_price),
            }
            st.session_state.pop("price_choice", None)
            st.session_state.pop("checked", None)

        prompt = st.session_state.get("prompt")
        if prompt:
            row = prompt["row"]
            mkt_price = prompt["mkt_price"]
            st.write(f"Strike {row['Strike']}, Exp {row['Expiry']:.2f}yr")
            st.write(
                f"Theoretical Call {row['Call Price']:.2f}, Market Call {mkt_price:.2f}"
            )
            choice = st.radio(
                "Is the market call overpriced or underpriced?",
                ("Overpriced", "Underpriced"),
                key="price_choice",
            )
            if st.button("Check Answer"):
                answer = (
                    "Overpriced" if mkt_price > row["Call Price"] else "Underpriced"
                )
                diff_pct = (mkt_price - row["Call Price"]) / row["Call Price"] * 100
                st.session_state.checked = {
                    "correct": choice == answer,
                    "answer": answer,
                    "diff_pct": diff_pct,
                }

            if "checked" in st.session_state:
                result = st.session_state.checked
                if result["correct"]:
                    st.write("Correct")
                else:
                    st.write(f"Incorrect, was {result['answer']}")
                st.write(f"Difference: {result['diff_pct']:.2f}%")

            st.write(
                f"Delta-neutral hedge: {-row['Call Delta']:.2f} shares; RevCon: {row['RevCon']:.2f}"
            )


elif page == "Put-Call Parity":
    st.header("Put-Call Parity Practice")
    if st.button("Generate New Parameters") or "pcp_params" not in st.session_state:
        st.session_state.pcp_params = parity.generate_parameters()
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
        fig = parity.payoff_diagram(params, diff)

def main():
    setup_page_config()
    initialize_session_state()

    st.title("📈 Options Practice App")
    st.markdown("---")

    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Mode",
            ("Options Chain", "Put-Call Parity", "Arbitrage Simulator", "Delta Hedging", "Quiz"),
            index=0
        )

        st.markdown("---")
        st.subheader("About")
        st.write("Practice options trading concepts with interactive simulations and quizzes.")

    if page == "Options Chain":
        options_chain_page()
    elif page == "Put-Call Parity":
        parity.put_call_parity_page()
    elif page == "Arbitrage Simulator":
        parity.arbitrage_simulator_page()
    elif page == "Delta Hedging":
        dh.delta_hedging_page()
    elif page == "Quiz":
        quiz.quiz_page()

if __name__ == "__main__":
    main()

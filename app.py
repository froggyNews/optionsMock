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

        if st.button("Random Prompt"):
            row = df_chain.sample(1).iloc[0]
            mkt_price = row["Call Price"] * (1 + np.random.uniform(-0.2, 0.2))
            st.write(f"Strike {row['Strike']}, Exp {row['Expiry']:.2f}yr, Market Price {mkt_price:.2f}")
            choice = st.radio("Call value vs Theoretical?", ("Overpriced", "Underpriced"))
            if st.button("Check Value"):
                answer = "Overpriced" if mkt_price > row["Call Price"] else "Underpriced"
                st.write("Correct" if choice == answer else f"Incorrect, was {answer}")
            st.write(f"Delta-neutral hedge: {-row['Call Delta']:.2f} shares; RevCon: {row['RevCon']:.2f}")

def main():
    setup_page_config()
    initialize_session_state()

    st.title("📈 Options Practice App")
    st.markdown("---")

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

elif page == "Delta Hedging":
    st.header("Delta Hedging Simulation")

    S0 = 100.0
    K = 100.0
    r = 0.01
    T = 1.0
    dt = 1 / 52

    if "dh_state" not in st.session_state:
        st.session_state.dh_state = dh.init_state(S0, K, r, T)

    auto_hedge = st.checkbox("Auto-Hedge using option delta", value=True)
    hedge_ratio = st.slider("Hedge Ratio (shares)", -2.0, 2.0, 0.0, step=0.1)

    col1, col2 = st.columns(2)
    if col1.button("Next Step"):
        st.session_state.dh_state = dh.update_state(
            st.session_state.dh_state,
            hedge_ratio,
            K,
            r,
            T,
            dt,
            auto_hedge=auto_hedge,
        )
    if col2.button("Reset"):
        st.session_state.dh_state = dh.init_state(S0, K, r, T)

    st.write(
        {
            "Stock": st.session_state.dh_state["S"],
            "Delta": st.session_state.dh_state["delta"],
            "Hedge": st.session_state.dh_state["hedge"],
            "PnL": st.session_state.dh_state["pnl"],
        }
    )

    fig = dh.plot_history(st.session_state.dh_state)
    st.pyplot(fig)

elif page == "Quiz":
    st.header("Quiz")
    if "quiz" not in st.session_state:
        q, opts, ans, idx = quiz.ask_question()
        st.session_state.quiz = {"q": q, "opts": opts, "ans": ans, "idx": idx}

    qdata = st.session_state.quiz
    st.write(qdata["q"])
    choice = st.radio("Answer", qdata["opts"])
    if st.button("Submit Answer"):
        correct = qdata["opts"].index(choice) == qdata["ans"]
        quiz.record_result(correct)
        st.write("Correct" if correct else "Incorrect")
        # load new question
        q, opts, ans, idx = quiz.ask_question()
        st.session_state.quiz = {"q": q, "opts": opts, "ans": ans, "idx": idx}

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

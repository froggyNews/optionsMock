import streamlit as st
import numpy as np

from option_pricing import call_price
import parity
import delta_hedging as dh
import quiz


st.title("Options Practice App")

page = st.sidebar.radio(
    "Select Mode",
    ("Put-Call Parity", "Delta Hedging", "Quiz"),
)

if page == "Put-Call Parity":
    st.header("Put-Call Parity Practice")
    if st.button("Generate New Parameters") or "pcp_params" not in st.session_state:
        st.session_state.pcp_params = parity.generate_parameters()
    params = st.session_state.pcp_params

    st.write(
        f"Spot (S) = {params['S']:.2f}, Strike (K) = {params['K']:.2f}, Call Price (C) = {params['C']:.2f}, "
        f"Put Price (P) = {params['P']:.2f}, r = {params['r']:.3f}, T = {params['T']:.2f}"
    )

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
        st.write(f"Difference: {diff:.2f}")
        fig = parity.payoff_diagram(params, diff)
        st.pyplot(fig)

elif page == "Delta Hedging":
    st.header("Delta Hedging Simulation")
    S0 = 100.0
    K = 100.0
    r = 0.01
    T = 1.0
    dt = 1 / 52

    if "dh_state" not in st.session_state:
        st.session_state.dh_state = dh.init_state(S0, K, r, T)

    hedge_ratio = st.slider("Hedge Ratio (shares)", -2.0, 2.0, 0.0, step=0.1)
    col1, col2 = st.columns(2)
    if col1.button("Next Step"):
        st.session_state.dh_state = dh.update_state(
            st.session_state.dh_state, hedge_ratio, K, r, T, dt
        )
    if col2.button("Reset"):
        st.session_state.dh_state = dh.init_state(S0, K, r, T)

    st.write(st.session_state.dh_state)
    st.line_chart(
        {
            "Stock": [st.session_state.dh_state["S"]],
            "Delta": [st.session_state.dh_state["delta"]],
        }
    )

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

    score, total = quiz.load_history()
    st.write(f"Score: {score}/{total}")

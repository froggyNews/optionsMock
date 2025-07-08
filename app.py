import streamlit as st
import numpy as np

from option_pricing import call_price
from options_chain import generate_chain
import parity
import delta_hedging as dh
import quiz
import trade_simulation as ts


st.title("Options Practice App")

page = st.sidebar.radio(
    "Select Mode",
    ("Options Chain", "Put-Call Parity", "Arbitrage Simulator", "Delta Hedging", "Quiz"),
)

if page == "Options Chain":
    st.header("Options Chain Builder")
    spot = st.number_input("Spot Price", value=100.0)
    r = st.number_input("Risk Free Rate", value=0.01)
    vol = st.number_input("Implied Volatility", value=0.2)
    width = st.number_input("Strike Width", value=5.0)
    strikes = np.arange(spot - 2 * width, spot + 2 * width + width, width)
    expiries_months = st.multiselect(
        "Expiry Months", options=[1, 2, 3], default=[1, 2, 3]
    )
    expiries = [m / 12 for m in expiries_months]
    if expiries:
        df_chain = generate_chain(spot, r, expiries, strikes, vol)
        st.dataframe(df_chain)
        if st.button("Random Prompt"):
            row = df_chain.sample(1).iloc[0]
            mkt_price = row["Call Price"] * (1 + np.random.uniform(-0.2, 0.2))
            st.write(
                f"Strike {row['Strike']}, Exp {row['Expiry']:.2f}yr, Market Price {mkt_price:.2f}"
            )
            choice = st.radio("Call value vs Theoretical?", ("Overpriced", "Underpriced"))
            if st.button("Check Value"):
                answer = "Overpriced" if mkt_price > row["Call Price"] else "Underpriced"
                st.write("Correct" if choice == answer else f"Incorrect, was {answer}")
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

elif page == "Arbitrage Simulator":
    st.header("Mock Trade Simulation")
    if st.button("Generate Scenario") or "sim_params" not in st.session_state:
        st.session_state.sim_params = parity.generate_parameters()
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

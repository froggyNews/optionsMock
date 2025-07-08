import streamlit as st
import numpy as np
import time

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

    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Mode",
            ("Options Chain", "Put-Call Parity", "Arbitrage Simulator", "Delta Hedging", "Quiz"),
            index=0
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
    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

    if (
        "quiz" not in st.session_state
        or st.session_state.quiz.get("difficulty") != difficulty
    ):
        q, idx = quiz.ask_question(difficulty=difficulty)
        st.session_state.quiz = {
            "q": q,
            "idx": idx,
            "start": time.time(),
            "difficulty": difficulty,
        }

    qdata = st.session_state.quiz
    st.write(f"Time remaining: {quiz.time_left(qdata['start'])}s")
    st.write(qdata["q"]["question"])
    choice = st.radio(
        "Answer",
        qdata["q"]["options"],
        key=f"choice_{qdata['idx']}",
    )
    if st.button("Submit Answer"):
        elapsed = time.time() - qdata["start"]
        timed_out = elapsed > quiz.TIME_LIMIT
        selected = qdata["q"]["options"].index(choice)
        correct = selected == qdata["q"]["answer"] and not timed_out
        quiz.record_result(correct, qdata["q"]["topic"])
        if timed_out:
            st.write("Time's up!")
        st.write("Correct!" if correct else "Incorrect.")
        st.write("Explanation:", qdata["q"]["explanation"])
        # load new question
        q, idx = quiz.ask_question(difficulty=difficulty)
        st.session_state.quiz = {
            "q": q,
            "idx": idx,
            "start": time.time(),
            "difficulty": difficulty,
        }

    score, total, accuracy, streak, high, by_topic = quiz.load_history()
    st.write(f"Score: {score}/{total}")
    st.write(f"Accuracy: {accuracy:.2%}")
    st.write(f"Current Streak: {streak}")
    st.write(f"High Score: {high}")
    st.write("Results by Topic:")
    for topic, stats in by_topic.items():
        st.write(f"{topic}: {stats['sum']}/{stats['count']}")


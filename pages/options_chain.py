import streamlit as st
import numpy as np
from utils.options_chain import generate_chain

st.header("Options Chain Builder")

difficulty = st.session_state.get("difficulty", "Standard")

spot = st.number_input("Spot Price", value=100.0)
r = st.number_input("Risk Free Rate", value=0.01)
vol = st.number_input("Implied Volatility", value=0.2)
width = st.number_input("Strike Width", value=5.0)
if difficulty == "Easy":
    spot = int(spot)
    width = int(width)

strikes = np.arange(spot - 2 * width, spot + 2 * width + width, width)
if difficulty == "Easy":
    strikes = strikes.astype(int)
expiries_months = st.multiselect("Expiry Months", options=[1, 2, 3], default=[1, 2, 3])
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


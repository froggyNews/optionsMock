import streamlit as st
from utils import delta_hedging as dh

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


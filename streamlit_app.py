import streamlit as st

st.set_page_config(page_title="Options Trainer")

st.title("Options Practice Suite")
st.write("Use the sidebar to select an activity.")

pages = [
    "parity",
    "arbitrage_simulator",
    "delta_hedging",
    "options_chain",
    "quiz",
    "interactive_trading",
]

for p in pages:
    st.sidebar.page_link(f"pages/{p}.py", label=p.replace("_", " ").title())

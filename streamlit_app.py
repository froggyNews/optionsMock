import streamlit as st

st.set_page_config(page_title="Options Trainer")

st.title("Options Practice Suite")
st.write("Use the button below to launch the interactive trader.")

# Only expose the interactive trading page for now
st.sidebar.page_link(
    "pages/interactive_trading.py", label="Interactive Trading"
)

# Provide a direct link from the home page
st.page_link(
    "pages/interactive_trading.py", label="Launch Interactive Trader", icon="▶️"
)

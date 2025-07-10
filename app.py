import streamlit as st
from utils.ui_config import difficulty_selector

st.set_page_config(page_title="Options Trainer")

PAGES = {
    "Market Taker": "pages/interactive_trader.py",
    "Market Maker": "pages/interactive_maker.py",
}


st.title("Options Practice Suite")
st.write("Select a module from the sidebar to begin.")

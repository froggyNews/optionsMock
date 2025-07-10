import streamlit as st
from utils.ui_config import difficulty_selector

st.set_page_config(page_title="Options Trainer")

PAGES = {
    "Market Taker": "pages/interactive_trader.py",
    "Market Maker": "pages/interactive_maker.py",
}

# Hide default Streamlit navigation
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.title("Practice Modules")
choice = st.sidebar.radio("Module", list(PAGES.keys()))

difficulty_selector()

if st.sidebar.button("Open Module"):
    st.switch_page(PAGES[choice])

st.title("Options Practice Suite")
st.write("Select a module from the sidebar to begin.")

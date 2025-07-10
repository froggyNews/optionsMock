import streamlit as st




def difficulty_selector() -> str:
    """Sidebar widget to choose difficulty level."""
    # 1. Seed a default on first run
    if "difficulty" not in st.session_state:
        st.session_state["difficulty"] = "Normal"

    # 2. Create the selectbox; it will read/write st.session_state["difficulty"]
    diff = st.sidebar.selectbox(
        "Difficulty",
        ["Easy", "Normal", "Hard"],
        index=["Easy", "Normal", "Hard"].index(st.session_state["difficulty"]),
        key="difficulty",
    )
    return diff



def taker_trade_form():
    """Form for market taker trade entry."""
    with st.form("taker_trade_form"):
        side = st.selectbox("Side", ["Buy", "Sell"])
        qty = st.number_input("Quantity", 1, 100, 1)
        submitted = st.form_submit_button("Execute Trade")
    if submitted:
        return {"side": side, "qty": int(qty)}
    return None


def maker_quote_form():
    """Form for market maker quoting."""
    with st.form("maker_quote_form"):
        bid = st.number_input("Bid", value=0.0)
        ask = st.number_input("Ask", value=0.0)
        qty = st.number_input("Size", 1, 100, 1)
        submitted = st.form_submit_button("Post Quote")
    if submitted:
        return {"bid": bid, "ask": ask, "qty": int(qty)}
    return None

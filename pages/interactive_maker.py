import numpy as np
import pandas as pd
import streamlit as st

from utils import greeks, option_pricing as op, scenario_generator
from utils.market_maker import MarketMaker
from utils.ui_config import difficulty_selector

st.set_page_config(page_title="Market Maker")

st.title("Market Maker Practice")

difficulty_selector()

if (
    st.button("Generate New Scenario", key="maker_new")
    or "scenario" not in st.session_state
):
    st.session_state.scenario = scenario_generator.generate_scenario()
    for key in ["maker_step1", "maker_step2", "maker_step3", "maker_step4"]:
        st.session_state.pop(key, None)

sc = st.session_state.scenario

call_delta = greeks.call_delta(sc["S"], sc["K"], sc["r"], sc["T"], sc["sigma"])
put_delta = greeks.put_delta(sc["S"], sc["K"], sc["r"], sc["T"], sc["sigma"])
call_theo = op.call_price(sc["S"], sc["K"], sc["r"], sc["T"], sc["sigma"])
put_theo = op.put_price(sc["S"], sc["K"], sc["r"], sc["T"], sc["sigma"])

call_edge = call_theo - sc["C_mkt"]
put_edge = put_theo - sc["P_mkt"]
combined_delta = call_delta + put_delta

discount_factor = np.exp(-sc["r"] * sc["T"])

st.subheader("Market Scenario")

env_data = {
    "Spot (S)": f"${sc['S']:.2f}",
    "Strike (K)": f"${sc['K']:.2f}",
    "Rate (r)": f"{sc['r']:.2%}",
    "Time to Expiration (T)": f"{sc['T']:.2f} yrs",
    "Volatility (σ)": f"{sc['sigma']:.2%}",
    "e^{-rT}": f"{discount_factor:.4f}",
}

st.markdown("### Market Environment")
for label, val in env_data.items():
    if label == "e^{-rT}":
        st.latex(rf"{label} = {val}")
    else:
        st.markdown(f"**{label}:** {val}")

option_data = {
    "Metric": ["Market Price", "Theoretical Price", "Delta"],
    "Call": [f"${sc['C_mkt']:.2f}", f"${call_theo:.2f}", f"{call_delta:.2f}"],
    "Put": [f"${sc['P_mkt']:.2f}", f"${put_theo:.2f}", "—"],
}
option_df = pd.DataFrame(option_data)
st.table(option_df)

st.markdown("### Step 1: Parity & Mispricing")
with st.form("maker_step1"):
    call_mid_in = st.number_input("1. Call quote midpoint", format="%.2f")
    put_mid_in = st.number_input("2. Put quote midpoint", format="%.2f")
    step1_submit = st.form_submit_button("Check Step 1")

if step1_submit:
    base_call = sc["C_mkt"] + 0.5 * call_edge
    base_put = sc["P_mkt"] + 0.5 * put_edge
    target = sc["S"] - sc["K"] * discount_factor
    diff = base_call - base_put
    adjust = diff - target
    correct_call = base_call - adjust / 2
    correct_put = base_put + adjust / 2
    ok = abs(call_mid_in - correct_call) < 0.1 and abs(put_mid_in - correct_put) < 0.1
    if ok:
        st.success("Midpoints maintain parity and capture edge.")
        st.session_state.maker_step1 = True
    else:
        st.error(f"Expected call {correct_call:.2f}, put {correct_put:.2f}")

if st.session_state.get("maker_step1"):
    st.markdown("### Step 2: Trade Strategy")
    with st.form("maker_step2"):
        lean_side = st.radio(
            "3. Which side will you lean into first?",
            ["Buy", "Sell"],
            horizontal=True,
        )
        lean_reason = st.selectbox(
            "4. Why?",
            ["Collect premium", "Hedge delta risk", "Manage inventory"],
        )
        step2_submit = st.form_submit_button("Check Step 2")
    if step2_submit:
        straddle_edge = call_edge + put_edge
        if abs(straddle_edge) < 0.05:
            correct_side, correct_reason = "Sell", "Manage inventory"
        elif straddle_edge > 0:
            correct_side, correct_reason = "Buy", "Hedge delta risk"
        else:
            correct_side, correct_reason = "Sell", "Collect premium"
        if lean_side == correct_side and lean_reason == correct_reason:
            st.success("Strategy aligned with edge.")
            st.session_state.maker_step2 = True
        else:
            st.error(f"Expected {correct_side} – {correct_reason}.")

if st.session_state.get("maker_step2"):
    st.markdown("### Step 3: Greek Risk Analysis")
    with st.form("maker_step3"):
        delta_in = st.number_input("5. Net delta from quotes", format="%.3f")
        hedge_in = st.number_input("6. Shares to hedge", format="%.0f")
        step3_submit = st.form_submit_button("Check Step 3")
    if step3_submit:
        correct_shares = -combined_delta * 100
        ok_delta = abs(delta_in - combined_delta) < 0.05
        ok_hedge = abs(hedge_in - correct_shares) <= 5
        if ok_delta:
            st.success("Delta correct")
        else:
            st.error(f"Expected delta {combined_delta:.3f}")
        if ok_hedge:
            st.success(f"Hedge {correct_shares:.0f} shares")
        else:
            st.error(f"Expected hedge {correct_shares:.0f}")
        st.session_state.maker_step3 = True

if st.session_state.get("maker_step3"):
    st.markdown("### Step 4: Risk Profile")
    with st.form("maker_step4"):
        fill_prob = st.slider("7. Expected fill probability (%)", 0, 100, 50)
        risk_choice = st.radio(
            "8. Overall risk level?",
            ["Low", "Medium", "High"],
            horizontal=True,
        )
        notes = st.text_area("9. Explain your reasoning")
        step4_submit = st.form_submit_button("Submit Step 4")
    if step4_submit:
        exposure = abs(combined_delta) * 100 * fill_prob / 100
        if exposure < 10:
            correct_risk = "Low"
        elif exposure < 30:
            correct_risk = "Medium"
        else:
            correct_risk = "High"
        if risk_choice == correct_risk:
            st.success("Risk assessment reasonable")
        else:
            st.error(f"Expected risk level {correct_risk}")
        st.session_state.maker_step4 = True

if st.session_state.get("maker_step4"):
    st.markdown("## Live Quoting Simulation")
    maker = MarketMaker(sc, call_delta, put_delta, call_theo, put_theo)
    maker.render()


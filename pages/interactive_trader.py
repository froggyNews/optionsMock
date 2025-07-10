import numpy as np
import pandas as pd
import streamlit as st

from utils import greeks, option_pricing as op, scenario_generator
from utils.market_taker import MarketTaker
from utils.ui_config import difficulty_selector

st.set_page_config(page_title="Market Taker")

st.title("Market Taker Practice")

difficulty_selector()

if st.button("Generate New Scenario", key="taker_new") or "scenario" not in st.session_state:
    st.session_state.scenario = scenario_generator.generate_scenario()
    for key in ["taker_step1", "taker_step2", "taker_step3", "taker_step4"]:
        st.session_state.pop(key, None)

sc = st.session_state.scenario

call_delta = greeks.call_delta(sc["S"], sc["K"], sc["r"], sc["T"], sc["sigma"])
put_delta = greeks.put_delta(sc["S"], sc["K"], sc["r"], sc["T"], sc["sigma"])
call_theo = op.call_price(sc["S"], sc["K"], sc["r"], sc["T"], sc["sigma"])
put_theo = op.put_price(sc["S"], sc["K"], sc["r"], sc["T"], sc["sigma"])

call_edge = call_theo - sc["C_mkt"]
put_edge = put_theo - sc["P_mkt"]
discount_factor = np.exp(-sc["r"] * sc["T"])
parity_gap = sc["C_mkt"] - sc["P_mkt"] - (sc["S"] - sc["K"] * discount_factor)

trader = MarketTaker(sc, call_delta, put_delta, call_theo, put_theo)

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
with st.form("taker_step1"):
    parity_in = st.number_input("1. Parity gap", format="%.3f")
    col1, col2 = st.columns(2)
    with col1:
        call_mis = st.radio(
            "2a. Call value", ["Cheap", "Fair", "Expensive"], index=1, horizontal=True
        )
    with col2:
        put_mis = st.radio(
            "2b. Put value", ["Cheap", "Fair", "Expensive"], index=1, horizontal=True
        )
    step1_submit = st.form_submit_button("Check Step 1")

if step1_submit:
    def assess(edge):
        if edge > 0.05:
            return "Cheap"
        elif edge < -0.05:
            return "Expensive"
        else:
            return "Fair"

    correct_call = assess(call_edge)
    correct_put = assess(put_edge)
    ok_parity = abs(parity_in - parity_gap) < 0.01
    ok_call = call_mis == correct_call
    ok_put = put_mis == correct_put
    if ok_parity and ok_call and ok_put:
        st.success("Step 1 correct")
        st.session_state.taker_step1 = True
    else:
        st.error(
            f"Expected parity {parity_gap:.3f}, call {correct_call}, put {correct_put}"
        )

if st.session_state.get("taker_step1"):
    st.markdown("### Step 2: Trade Strategy")
    with st.form("taker_step2"):
        call_action = st.radio(
            "3a. Call action", ["Buy call", "Sell call", "No call trade"], horizontal=True
        )
        put_action = st.radio(
            "3b. Put action", ["Buy put", "Sell put", "No put trade"], horizontal=True
        )
        exp_profit = st.number_input("4. Expected profit per contract ($)", format="%.2f")
        step2_submit = st.form_submit_button("Check Step 2")

    if step2_submit:
        def get_correct_actions():
            if abs(parity_gap) > 0.1:
                if call_edge + put_edge > 0:
                    return ("Buy call", "Buy put")
                else:
                    return ("Sell call", "Sell put")
            c_act = "Buy call" if call_edge > 0.05 else "Sell call" if call_edge < -0.05 else "No call trade"
            p_act = "Buy put" if put_edge > 0.05 else "Sell put" if put_edge < -0.05 else "No put trade"
            return (c_act, p_act)

        correct_call_act, correct_put_act = get_correct_actions()

        expected_edge = (
            abs(call_edge + put_edge)
            if correct_call_act.startswith("Buy") and correct_put_act.startswith("Buy")
            or correct_call_act.startswith("Sell") and correct_put_act.startswith("Sell")
            else abs(call_edge) if "call" in correct_call_act else abs(put_edge)
        )

        ok_call = call_action == correct_call_act
        ok_put = put_action == correct_put_act
        ok_profit = abs(exp_profit - expected_edge) < 0.1

        if ok_call and ok_put and ok_profit:
            st.success("Strategy sound")
            st.session_state.taker_step2 = True
            st.session_state.taker_call_action = call_action
            st.session_state.taker_put_action = put_action
        else:
            st.error(
                f"Expected {correct_call_act}/{correct_put_act} profit ${expected_edge:.2f}"
            )

if st.session_state.get("taker_step2"):
    st.markdown("### Step 3: Greek Risk Analysis")
    with st.form("taker_step3"):
        delta_in = st.number_input("5. Net delta", format="%.3f")
        hedge_shares = st.number_input("6. Shares to hedge", format="%.0f")
        step3_submit = st.form_submit_button("Check Step 3")

    if step3_submit:
        def action_delta(action, delta):
            if action.startswith("Buy"):
                return delta
            elif action.startswith("Sell"):
                return -delta
            return 0

        call_action_val = st.session_state.get("taker_call_action")
        put_action_val = st.session_state.get("taker_put_action")
        correct_delta = action_delta(call_action_val, call_delta) + action_delta(put_action_val, put_delta)
        correct_hedge = -correct_delta * 100

        ok_delta = abs(delta_in - correct_delta) < 0.05
        ok_hedge = abs(hedge_shares - correct_hedge) <= 5
        if ok_delta:
            st.success("Delta correct")
        else:
            st.error(f"Expected delta {correct_delta:.3f}")
        if ok_hedge:
            st.success(f"Hedge {correct_hedge:.0f} shares")
        else:
            st.error(f"Expected hedge {correct_hedge:.0f}")
        st.session_state.taker_step3 = True
        st.session_state.taker_delta = delta_in

if st.session_state.get("taker_step3"):
    st.markdown("### Step 4: Risk Profile")
    with st.form("taker_step4"):
        risk_lvl = st.radio(
            "7. Overall risk level?", ["Low", "Medium", "High"], horizontal=True
        )
        notes = st.text_area("8. Explain your reasoning")
        step4_submit = st.form_submit_button("Submit Step 4")
    if step4_submit:
        exposure = abs(st.session_state.get("taker_delta", 0)) * 100
        if exposure < 10:
            correct = "Low"
        elif exposure < 30:
            correct = "Medium"
        else:
            correct = "High"
        if risk_lvl == correct:
            st.success("Assessment recorded")
        else:
            st.error(f"Expected risk level {correct}")
        st.session_state.taker_step4 = True

if st.session_state.get("taker_step4"):
    st.markdown("## Live Trading Simulation")
    trader.render()

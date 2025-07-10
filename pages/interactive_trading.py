import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils import trade_simulation as ts
from utils import scenario_generator
from utils import greeks
from utils import option_pricing as op
from utils.live_trader import LiveTrader

# Page configuration
st.set_page_config(
    page_title="Options Trading Simulator - Kavita",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Header
st.title("Options Trading Simulator")
st.caption("Personal Training Tool for Options Market Making Skills")

# Scenario Generation
if st.button("Generate New Scenario", key="generate_new_scenario") or "scenario" not in st.session_state:
    st.session_state.scenario = scenario_generator.generate_scenario()
    # Reset all state when new scenario is generated
    for key in ['pos_greeks', 'checked_greeks', 'user_sel', 'step1_complete', 'step2_complete', 'step3_complete', 'trading_stage', 'initial_position', 'market_events', 'event_response']:
        st.session_state.pop(key, None)

sc = st.session_state.scenario

# --- Section: Market Scenario ---
st.subheader("Market Scenario")

# --- Calculated Values ---
call_delta = greeks.call_delta(sc['S'], sc['K'], sc['r'], sc['T'], sc['sigma'])
call_theo = op.call_price(sc['S'], sc['K'], sc['r'], sc['T'], sc['sigma'])
put_theo = op.put_price(sc['S'], sc['K'], sc['r'], sc['T'], sc['sigma'])
discount_factor = np.exp(-sc['r'] * sc['T'])

# --- Table 1: Market Parameters ---
env_data = {
    "Spot (S)": f"${sc['S']:.2f}",
    "Strike (K)": f"${sc['K']:.2f}",
    "Rate (r)": f"{sc['r']:.2%}",
    "Time to Expiration (T)": f"{sc['T']:.2f} yrs",
    "Volatility (σ)": f"{sc['sigma']:.2%}",
    "e^{-rT}": f"{discount_factor:.4f}"
}
env_df = pd.DataFrame(env_data, index=["Value"]).T
# --- Display Market Environment ---
st.markdown("### Market Environment")

for label, val in env_data.items():
    if label == "e^{-rT}":
        # render the discount factor with LaTeX
        st.latex(rf"{label} = {val}")
    else:
        # bold the label and show the value
        st.markdown(f"**{label}:** {val}")


# --- Table 2: Option Pricing Data ---
option_data = {
    "Metric": ["Market Price", "Theoretical Price", "Delta"],
    "Call": [f"${sc['C_mkt']:.2f}", f"${call_theo:.2f}", f"{call_delta:.2f}"],
    "Put": [f"${sc['P_mkt']:.2f}", f"${put_theo:.2f}", "—"]
}
option_df = pd.DataFrame(option_data)
st.table(option_df)

# --- Section: Market Analysis Training ---
st.subheader("Market Analysis Training")

# Calculate all the key metrics
put_delta = greeks.put_delta(sc["S"], sc["K"], sc["r"], sc["T"], sc["sigma"])
call_edge = call_theo - sc["C_mkt"]
put_edge = put_theo - sc["P_mkt"]
discount_factor = np.exp(-sc["r"] * sc["T"])
parity_gap = sc["C_mkt"] - sc["P_mkt"] - (sc["S"] - sc["K"] * discount_factor)
straddle_edge = call_edge + put_edge
straddle_delta = call_delta + put_delta

# --- Step 1: Initial Assessment ---
st.markdown("### Put-Call Parity")

with st.form("step1_form"):
    # Question 1: Parity check
    st.latex(r"C - P - \left(S - K e^{-rT} \right)")
    user_parity = st.number_input(
        "1. What is the value of the put-call parity gap?",
        format="%.3f",
        help="This should be ~0 in a fair market. A nonzero value suggests arbitrage."
    )

    # Question 2: Option Mispricing
    st.markdown("### 2. Mispricing Assessment")
    col1, col2 = st.columns(2)

    with col1:
        call_mispricing = st.radio(
            "Call Value:",
            ["Cheap", "Fair", "Expensive"],
            index=1,
            horizontal=True
        )

    with col2:
        put_mispricing = st.radio(
            "Put Value:",
            ["Cheap", "Fair", "Expensive"],
            index=1,
            horizontal=True
        )

    step1_check = st.form_submit_button("Check Step 1")

# --- Step 1 Feedback ---
if step1_check:
    st.markdown("#### Step 1 Results:")

    # Parity check
    st.latex(r"\text{Parity Gap} = C - P - (S - K e^{-rT})")
    if abs(user_parity - parity_gap) < 0.01:
        st.success(f"Correct parity gap: {parity_gap:.3f}")
        if abs(parity_gap) > 0.05:
            st.info("**ARBITRAGE ALERT**: Significant parity violation detected!")
    else:
        st.error(f"Incorrect parity gap. Expected: {parity_gap:.3f}, Got: {user_parity:.3f}")

    # Option mispricing assessment
    def assess_price(edge):
        if edge > 0.05:
            return "Cheap"
        elif edge < -0.05:
            return "Expensive"
        else:
            return "Fair"

    correct_call = assess_price(call_edge)
    correct_put = assess_price(put_edge)

    call_correct = call_mispricing == correct_call
    put_correct = put_mispricing == correct_put

    if call_correct and put_correct:
        st.success("Correct mispricing assessment for both call and put.")
    else:
        st.error("Incorrect mispricing assessment.")
        st.info(f"Expected → Call: {correct_call}, Put: {correct_put}")
        st.info(f"Call edge: {call_edge:+.3f}, Put edge: {put_edge:+.3f}")

    # Show theoretical prices with math
    st.markdown("#### Price Analysis:")
    st.markdown("**Call:**")
    st.latex(fr"\text{{Call}}_{{theo}} = {call_theo:.2f},\quad \text{{Market}} = {sc['C_mkt']:.2f},\quad \text{{Edge}} = {call_edge:+.3f}")
    st.markdown("**Put:**")
    st.latex(fr"\text{{Put}}_{{theo}} = {put_theo:.2f},\quad \text{{Market}} = {sc['P_mkt']:.2f},\quad \text{{Edge}} = {put_edge:+.3f}")
    st.markdown("**Key Insight:**")
    st.markdown(f"- Call is **{correct_call}**, Put is **{correct_put}**")

    # Store step 1 completion
    st.session_state.step1_complete = True


# --- Step 2: Trade Strategy (only show after Step 1) ---
if st.session_state.get("step1_complete", False):
    st.markdown("### Step 2: Trade Strategy")

    with st.form("step2_form"):
        # Call action selector
        call_action = st.radio(
            "4a. Call Action:",
            ["Buy call", "Sell call", "No call trade"],
            horizontal=True
        )

        # Put action selector
        put_action = st.radio(
            "4b. Put Action:",
            ["Buy put", "Sell put", "No put trade"],
            horizontal=True
        )

        # Expected profit
        expected_profit = st.number_input(
            "5. What profit do you expect per contract? ($)",
            format="%.2f"
        )

        step2_check = st.form_submit_button("Check Step 2")

    # --- Step 2 Feedback ---
    if step2_check:
        st.markdown("#### Step 2 Results:")

        # Derive the “combined” correct action
        def get_correct_actions():
            # decide straddle/no-trade first
            if abs(parity_gap) > 0.1:
                if straddle_edge > 0:
                    return ("Buy call", "Buy put")
                else:
                    return ("Sell call", "Sell put")
            # otherwise individual edges
            c_act = "Buy call" if call_edge > 0.05 else "Sell call" if call_edge < -0.05 else "No call trade"
            p_act = "Buy put"  if put_edge  > 0.05 else "Sell put" if put_edge  < -0.05 else "No put trade"
            return (c_act, p_act)

        correct_call, correct_put = get_correct_actions()

        # Check call
        if call_action == correct_call:
            st.success(f"Call action correct: {correct_call}")
        else:
            st.error(f"Call action wrong. Expected: {correct_call}, Got: {call_action}")

        # Check put
        if put_action == correct_put:
            st.success(f"Put action correct: {correct_put}")
        else:
            st.error(f"Put action wrong. Expected: {correct_put}, Got: {put_action}")

        # Profit check
        expected_edge = (
            abs(straddle_edge)
            if (correct_call.endswith("call") and correct_put.endswith("put") and correct_call.split()[0] == correct_put.split()[0])
            else abs(call_edge) if correct_call.endswith("call")
            else abs(put_edge)
        )
        if abs(expected_profit - expected_edge) < 0.1:
            st.success("Profit expectation reasonable")
        else:
            st.error(f"Expected profit ~${expected_edge:.2f}, got ${expected_profit:.2f}")

        st.session_state.step2_complete = True

# --- Step 3: Greek Risk Analysis (only show after Step 2) ---
if st.session_state.get("step2_complete", False):
    st.markdown("### Step 3: Greek Risk Analysis")

    with st.form("step3_form"):
        # Question 7: Delta exposure
        expected_delta = st.number_input(
            "7. What total delta exposure will your combined trade create?",
            format="%.3f",
            help="Positive = net long delta, Negative = net short delta"
        )

        # Question 8: Hedge requirement
        hedge_shares = st.number_input(
            "8. How many shares do you need to hedge this delta? (negative = short)",
            format="%.0f"
        )

        step3_check = st.form_submit_button("Check Step 3")

    if step3_check:
        st.markdown("#### Step 3 Results:")

        # Compute correct combined delta from call_action and put_action
        def action_delta(action, delta):
            if action.startswith("Buy"):
                return delta
            elif action.startswith("Sell"):
                return -delta
            else:  # "No ... trade"
                return 0

        correct_delta = (
            action_delta(call_action, call_delta) +
            action_delta(put_action, put_delta)
        )

        # Check delta exposure
        if abs(expected_delta - correct_delta) < 0.05:
            st.success(f"Correct delta: {correct_delta:.3f}")
        else:
            st.error(f"Expected delta: {correct_delta:.3f}, Got: {expected_delta:.3f}")

        # Hedge calculation: delta × 100 contracts → shares
        correct_hedge = -correct_delta * 100
        if abs(hedge_shares - correct_hedge) < 10:
            st.success(f"Correct hedge: {correct_hedge:.0f} shares")
        else:
            st.error(f"Expected hedge: {correct_hedge:.0f} shares, Got: {hedge_shares:.0f}")

        st.session_state.step3_complete = True

# --- Step 4: Complete Risk Profile (only after Step 3) ---
if st.session_state.get("step3_complete", False):
    st.markdown("### Step 4: Complete Risk Profile")

    # Calculate position Greeks based on the call_action & put_action
    def get_position_greeks():
        total = {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'rho': 0}

        # Helper to add/subtract each Greek
        def apply_greeks(multiplier, greek_funcs):
            for g, fn in greek_funcs.items():
                total[g] += multiplier * fn

        # Call leg
        call_mult =  1 if call_action == "Buy call" else -1 if call_action == "Sell call" else 0
        if call_mult:
            apply_greeks(call_mult, {
                'delta': call_delta,
                'gamma': greeks.gamma(sc['S'], sc['K'], sc['r'], sc['T'], sc['sigma']),
                'theta': greeks.call_theta(sc['S'], sc['K'], sc['r'], sc['T'], sc['sigma']),
                'vega':  greeks.vega(sc['S'], sc['K'], sc['r'], sc['T'], sc['sigma']),
                'rho':   greeks.call_rho(sc['S'], sc['K'], sc['r'], sc['T'], sc['sigma']),
            })

        # Put leg
        put_mult =  1 if put_action  == "Buy put"  else -1 if put_action  == "Sell put"  else 0
        if put_mult:
            apply_greeks(put_mult, {
                'delta': put_delta,
                'gamma': greeks.gamma(sc['S'], sc['K'], sc['r'], sc['T'], sc['sigma']),
                'theta': greeks.put_theta(sc['S'], sc['K'], sc['r'], sc['T'], sc['sigma']),
                'vega':  greeks.vega(sc['S'], sc['K'], sc['r'], sc['T'], sc['sigma']),
                'rho':   greeks.put_rho(sc['S'], sc['K'], sc['r'], sc['T'], sc['sigma']),
            })

        return total

    pos_greeks = get_position_greeks()

    # Display Greeks with interpretations
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Greek Values")
        for greek, value in pos_greeks.items():
            level = "High" if abs(value) > 0.3 else "Medium" if abs(value) > 0.1 else "Low"
            st.write(f"**{greek.title()}**: {value:.4f} ({level})")

    with col2:
        st.markdown("#### Risk Interpretations")
        st.write(f"**Delta**: {pos_greeks['delta']:.3f} → {abs(pos_greeks['delta']*100):.0f} share equivalent")
        if abs(pos_greeks['gamma']) > 0.1:
            st.write("**High Gamma**: Delta will shift rapidly with stock moves.")
        if abs(pos_greeks['theta']) > 0.05:
            st.write(f"**Time Decay**: Losing ${abs(pos_greeks['theta']):.2f}/day.")
        if abs(pos_greeks['vega']) > 0.1:
            st.write(f"**Vega Sensitive**: ${abs(pos_greeks['vega']):.2f} per 1% vol change.")
        if abs(pos_greeks['rho']) > 0.1:
            st.write(f"**Rho Impact**: ${abs(pos_greeks['rho']):.2f} per 1% rate change.")

    # Overall risk profile
    risk_flags = sum(1 for v in pos_greeks.values() if abs(v) > 0.2)
    if risk_flags == 0:
        st.success("**Low Risk Trade** – well balanced Greek exposures.")
    elif risk_flags <= 2:
        st.info("**Medium Risk Trade** – monitor key Greeks.")
    else:
        st.warning("**High Risk Trade** – multiple significant exposures.")

    st.markdown("---")
    st.success("**Analysis Complete!** Proceed to live trading simulation below.")


# Initialize trading stages
if "trading_stage" not in st.session_state:
    st.session_state.trading_stage = "initial"
    st.session_state.initial_position = None
    st.session_state.market_events = []
    st.session_state.pnl_history = []

locked = not st.session_state.get("step3_complete", False)
if locked:
    st.markdown("<div style='opacity:0.4; pointer-events: none;'>", unsafe_allow_html=True)

# --- Live Trading Simulation ---
st.title("Live Trading Simulation" + (" 🔒" if locked else ""))
if locked:
    st.info("Complete Step 3 to unlock the live trading simulator.")
else:
    trader = LiveTrader(sc, call_delta, put_delta, call_theo, put_theo)
    trader.render()

    # --- Training Guide Section ---
    with st.expander("Training Guide - How to Use This Simulator"):
        st.markdown("""
        ### Training Workflow
        
        1. **Market Analysis**: Work through the progressive assessment questions to identify trading opportunities
        2. **Initial Trade**: Enter your position based on the opportunity you identified
        3. **Market Events**: Respond to changing market conditions in real-time
        4. **Performance Review**: Learn from detailed feedback and scoring
        """)

    if locked:
        st.markdown("</div>", unsafe_allow_html=True)

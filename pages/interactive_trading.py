import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from utils import trade_simulation as ts
from utils import scenario_generator
from utils import greeks
from utils import option_pricing as op

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
    # Track current stage
    stage = st.session_state.trading_stage

    if stage == "initial":
        st.subheader("Initial Market Setup")
        
        # Display initial market data
        st.info(fr"""
        **Initial Market Conditions:**
        - Stock: \${sc['S']:.2f}
        - Call Market: \${sc['C_mkt']:.2f} | Theo: \${call_theo:.2f}
        - Put Market: \${sc['P_mkt']:.2f} | Theo: \${put_theo:.2f}
        - Time to expiry: {sc['T']:.2f} years
        - Volatility: {sc['sigma']:.1%}
        """)
        
        # Quick opportunity assessment
        with st.form("initial_assessment"):
            st.markdown("### Quick Market Assessment")
            
            opportunity = st.selectbox(
                "What's the primary opportunity?",
                ["Buy call", "Sell call", "Buy put", "Sell put", "Buy straddle", "Sell straddle", "No clear edge"]
            )
            
            position_size = st.selectbox(
                "Position size?",
                ["1 contract", "2 contracts", "5 contracts", "10 contracts"]
            )
            
            hedge_decision = st.selectbox(
                "Delta hedge strategy?",
                ["Hedge immediately", "Hedge after 1% move", "Stay unhedged", "Partial hedge"]
            )
            
            if st.form_submit_button("Enter Initial Position"):
                # Store initial position
                st.session_state.initial_position = {
                    'trade': opportunity,
                    'size': int(position_size.split()[0]),
                    'hedge_strategy': hedge_decision,
                    'entry_spot': sc['S'],
                    'entry_time': sc['T']
                }
                
                # Calculate initial P&L and Greeks
                pos_delta = 0
                if "call" in opportunity:
                    pos_delta = call_delta * (1 if "buy" in opportunity.lower() else -1) * st.session_state.initial_position['size']
                elif "put" in opportunity:
                    pos_delta = put_delta * (1 if "buy" in opportunity.lower() else -1) * st.session_state.initial_position['size']
                elif "straddle" in opportunity:
                    pos_delta = straddle_delta * (1 if "buy" in opportunity.lower() else -1) * st.session_state.initial_position['size']
                
                st.session_state.initial_position['delta'] = pos_delta
                st.session_state.trading_stage = "market_event"
                st.rerun()

    elif stage == "market_event":
        st.subheader("Market Event!")
        
        # Generate random market event
        if not st.session_state.market_events:
            import random
            events = [
                {
                    'type': 'stock_move',
                    'description': 'Stock gaps up 3% on earnings beat',
                    'new_spot': sc['S'] * 1.03,
                    'vol_change': -0.05,  # Vol drops after earnings
                    'time_passed': 0.01  # 1 day passed
                },
                {
                    'type': 'vol_spike',
                    'description': 'Market volatility spikes due to Fed announcement',
                    'new_spot': sc['S'] * 0.995,  # Small move down
                    'vol_change': 0.15,  # Vol jumps
                    'time_passed': 0.005  # Half day
                },
                {
                    'type': 'time_decay',
                    'description': 'Two weeks pass with sideways action',
                    'new_spot': sc['S'] * random.uniform(0.98, 1.02),
                    'vol_change': -0.03,  # Vol drops slightly
                    'time_passed': 0.04  # Two weeks
                },
                {
                    'type': 'gap_down',
                    'description': 'Stock gaps down 2.5% on sector news',
                    'new_spot': sc['S'] * 0.975,
                    'vol_change': 0.08,
                    'time_passed': 0.01
                }
            ]
            
            st.session_state.market_events = [random.choice(events)]
        
        event = st.session_state.market_events[0]
        
        # Display the event
        st.warning(f"**MARKET EVENT**: {event['description']}")
        
        # Calculate new market conditions
        new_spot = event['new_spot']
        new_vol = max(0.1, sc['sigma'] + event['vol_change'])
        new_time = max(0.01, sc['T'] - event['time_passed'])
        
        # Recalculate option values
        new_call_theo = op.call_price(new_spot, sc['K'], sc['r'], new_time, new_vol)
        new_put_theo = op.put_price(new_spot, sc['K'], sc['r'], new_time, new_vol)
        new_call_delta = greeks.call_delta(new_spot, sc['K'], sc['r'], new_time, new_vol)
        new_put_delta = greeks.put_delta(new_spot, sc['K'], sc['r'], new_time, new_vol)
        
        # Calculate position P&L
        def calculate_pnl():
            pos = st.session_state.initial_position
            pnl = 0
            
            if "buy call" in pos['trade']:
                pnl = (new_call_theo - call_theo) * pos['size'] * 100
            elif "sell call" in pos['trade']:
                pnl = (call_theo - new_call_theo) * pos['size'] * 100
            elif "buy put" in pos['trade']:
                pnl = (new_put_theo - put_theo) * pos['size'] * 100
            elif "sell put" in pos['trade']:
                pnl = (put_theo - new_put_theo) * pos['size'] * 100
            elif "buy straddle" in pos['trade']:
                pnl = ((new_call_theo - call_theo) + (new_put_theo - put_theo)) * pos['size'] * 100
            elif "sell straddle" in pos['trade']:
                pnl = ((call_theo - new_call_theo) + (put_theo - new_put_theo)) * pos['size'] * 100
                
            return pnl
        
        current_pnl = calculate_pnl()
        
        # Display new market state
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Before Event")
            st.write(f"Stock: ${sc['S']:.2f}")
            st.write(f"Vol: {sc['sigma']:.1%}")
            st.write(f"Time: {sc['T']:.3f} years")
            st.write(f"Call Theo: ${call_theo:.2f}")
            st.write(f"Put Theo: ${put_theo:.2f}")
        
        with col2:
            st.markdown("#### After Event")
            st.write(f"Stock: ${new_spot:.2f} ({((new_spot/sc['S'])-1)*100:+.1f}%)")
            st.write(f"Vol: {new_vol:.1%} ({(new_vol-sc['sigma'])*100:+.1f}%)")
            st.write(f"Time: {new_time:.3f} years")
            st.write(f"Call Theo: ${new_call_theo:.2f}")
            st.write(f"Put Theo: ${new_put_theo:.2f}")
        
        # Show P&L impact
        pnl_status = "Profit" if current_pnl > 0 else "Loss" if current_pnl < 0 else "Breakeven"
        st.markdown(f"### Position P&L: ${current_pnl:+,.0f} ({pnl_status})")
        

        # RESPONSE FORM (renamed so it doesn't clash with session_state key)
        with st.form("event_response_form"):
            st.markdown("### How Do You Respond?")
            risk_level = st.selectbox(
                "1. How would you rate your current risk level?",
                ["Low risk - hold position", "Medium risk - monitor closely", "High risk - need to adjust", "Extreme risk - close immediately"]
            )
            new_delta_guess = st.number_input(
                "2. What's your new position delta approximately?",
                format="%.2f"
            )
            action = st.selectbox(
                "3. What action will you take?",
                ["Hold position unchanged", "Add to position", "Reduce position size", "Close position", "Hedge with stock", "Roll to different strike", "Add hedging options"]
            )
            if action in ["Hedge with stock", "Add hedging options"]:
                hedge_amount = st.number_input(
                    "How much hedge? (shares if stock, contracts if options)",
                    format="%.0f"
                )
            else:
                hedge_amount = 0
            urgency = st.selectbox(
                "4. How urgent is this action?",
                ["Execute immediately", "Wait for better pricing", "End of day is fine", "Monitor and decide later"]
            )

            if st.form_submit_button("Execute Response"):
                # … compute correct_new_delta, current_pnl, etc. …
                st.session_state.event_response = {
                    'risk_assessment': risk_level,
                    'delta_guess': new_delta_guess,
                    'action': action,
                    'hedge_amount': hedge_amount,
                    'urgency': urgency,
                    'correct_delta': new_call_delta,
                    'actual_pnl': current_pnl,
                    'new_market_data': {
                        'spot': new_spot,
                        'vol': new_vol,
                        'time': new_time,
                        'call_theo': new_call_theo,
                        'put_theo': new_put_theo
                    }
                }
                st.session_state.trading_stage = "feedback"
                st.rerun()


    elif stage == "feedback":
        st.subheader("Response Analysis")
        
        response = st.session_state.event_response
        
        # Scorecard
        st.markdown("### Scorecard")
        score = 0
        total_points = 5
        actual_pnl = response["actual_pnl"]

        # 1. Risk assessment
        risk_label = response["risk_assessment"]
        if abs(actual_pnl) > 1000 and "High risk" in risk_label:
            st.write("Risk assessment: correctly identified high risk.")
            score += 1
        elif abs(actual_pnl) < 500 and "Low risk" in risk_label:
            st.write("Risk assessment: correctly identified low risk.")
            score += 1
        elif "Medium risk" in risk_label:
            st.write("Risk assessment: reasonable assessment.")
            score += 0.5
        else:
            st.write(f"Risk assessment: reconsider with P&L of ${actual_pnl:+,.0f}.")

        # 2. Delta estimate
        delta_error = abs(response["delta_guess"] - response["correct_delta"])
        if delta_error <= abs(response["correct_delta"]) * 0.2:
            st.write(f"Delta estimate: within acceptable range (actual {response['correct_delta']:.2f}).")
            score += 1
        else:
            st.write(f"Delta estimate: off by {delta_error:.2f}. Actual: {response['correct_delta']:.2f}.")

        # 3. Action appropriateness
        action = response["action"]
        if actual_pnl < -1000 and action in ["Reduce position size", "Close position", "Hedge with stock"]:
            st.write("Action choice: appropriate defensive move.")
            score += 1
        elif abs(actual_pnl) < 500 and action in ["Hold position unchanged", "Monitor and decide later"]:
            st.write("Action choice: reasonable to hold.")
            score += 1
        elif actual_pnl > 1000 and action in ["Hold position unchanged", "Add to position"]:
            st.write("Action choice: reasonable to add to a winning trade.")
            score += 1
        else:
            st.write("Action choice: consider alignment with your risk view.")
            score += 0.5

        # 4. Hedge sizing
        if action == "Hedge with stock":
            ideal_hedge = abs(response["correct_delta"]) * 100
            hedge_amt = response["hedge_amount"]
            if abs(hedge_amt - ideal_hedge) <= ideal_hedge * 0.3:
                st.write("Hedge sizing: appropriate.")
                score += 1
            else:
                st.write(f"Hedge sizing: expected ~{ideal_hedge:.0f}, got {hedge_amt:.0f}.")
        else:
            score += 1  # full credit if no hedge needed

        # 5. Urgency
        urgency = response["urgency"]
        if abs(actual_pnl) > 2000 and "immediately" in urgency:
            st.write("Urgency: appropriate for large P&L.")
            score += 1
        elif abs(actual_pnl) < 1000 and "Monitor" in urgency:
            st.write("Urgency: reasonable patience.")
            score += 1
        else:
            st.write("Urgency: consider matching to P&L impact.")
            score += 0.5

        # Final score
        percentage = (score / total_points) * 100
        st.markdown(f"**Final Score:** {score:.1f}/{total_points} ({percentage:.0f}%)")

        # Insights by event type
        st.markdown("### Additional Insights")
        event_type = st.session_state.market_events[0]["type"]
        insights = {
            "stock_move": "- Watch gamma: large moves shift delta significantly.\n- Volatility often drops after earnings.",
            "vol_spike": "- Long options gain, short options lose.\n- Hedging costs rise with higher vol.",
            "time_decay": "- Theta accelerates near expiration.\n- Shorts benefit from time decay.",
            "gap_down": "- Sudden moves spike vega P&L.\n- Determine if move is sector-specific or market-wide."
        }
        st.write(insights.get(event_type, "Review your decision in context of the market event."))

        # Continue or reset

        # Continue or reset
        col1, col2 = st.columns(2)
        if col1.button("Next Event"):
            st.session_state.trading_stage = "second_event"
            st.rerun()
        if col2.button("Start New Scenario"):
            for key in ['trading_stage', 'initial_position', 'market_events', 'event_response',
                        'step1_complete', 'step2_complete', 'step3_complete']:
                st.session_state.pop(key, None)
            st.rerun()

    elif stage == "second_event":
        st.subheader("Second Market Event!")
        
        # Generate follow-up event based on current position
        follow_up_events = [
            {
                'type': 'volatility_collapse',
                'description': 'Vol crush: Market calms down, volatility drops 40%',
                'vol_multiplier': 0.6,
                'spot_change': 1.005,
                'time_passed': 0.02
            },
            {
                'type': 'whipsaw',
                'description': 'Market whipsaws: Stock reverses previous move',
                'vol_multiplier': 1.2,
                'spot_change': 0.985 if st.session_state.market_events[0]['new_spot'] > sc['S'] else 1.015,
                'time_passed': 0.01
            },
            {
                'type': 'acceleration',
                'description': 'Trend accelerates: Move continues in same direction',
                'vol_multiplier': 1.1,
                'spot_change': 1.02 if st.session_state.market_events[0]['new_spot'] > sc['S'] else 0.98,
                'time_passed': 0.015
            }
        ]
        
        import random
        second_event = random.choice(follow_up_events)
        
        st.warning(f"**SECOND EVENT**: {second_event['description']}")
        
        # Calculate new conditions after second event
        first_event_data = st.session_state.event_response['new_market_data']
        
        second_spot = first_event_data['spot'] * second_event['spot_change']
        second_vol = max(0.1, first_event_data['vol'] * second_event['vol_multiplier'])
        second_time = max(0.005, first_event_data['time'] - second_event['time_passed'])
        
        # Recalculate option values after second event
        second_call_theo = op.call_price(second_spot, sc['K'], sc['r'], second_time, second_vol)
        second_put_theo = op.put_price(second_spot, sc['K'], sc['r'], second_time, second_vol)
        second_call_delta = greeks.call_delta(second_spot, sc['K'], sc['r'], second_time, second_vol)
        second_put_delta = greeks.put_delta(second_spot, sc['K'], sc['r'], second_time, second_vol)
        
        # Calculate cumulative P&L
        def calculate_cumulative_pnl():
            pos = st.session_state.initial_position
            pnl = 0
            
            if "buy call" in pos['trade']:
                pnl = (second_call_theo - call_theo) * pos['size'] * 100
            elif "sell call" in pos['trade']:
                pnl = (call_theo - second_call_theo) * pos['size'] * 100
            elif "buy put" in pos['trade']:
                pnl = (second_put_theo - put_theo) * pos['size'] * 100
            elif "sell put" in pos['trade']:
                pnl = (put_theo - second_put_theo) * pos['size'] * 100
            elif "buy straddle" in pos['trade']:
                pnl = ((second_call_theo - call_theo) + (second_put_theo - put_theo)) * pos['size'] * 100
            elif "sell straddle" in pos['trade']:
                pnl = ((call_theo - second_call_theo) + (put_theo - second_put_theo)) * pos['size'] * 100
                
            return pnl
        
        cumulative_pnl = calculate_cumulative_pnl()
        first_event_pnl = st.session_state.event_response['actual_pnl']
        second_event_pnl = cumulative_pnl - first_event_pnl
        
        # Display market progression
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### Original")
            st.write(f"Stock: ${sc['S']:.2f}")
            st.write(f"Vol: {sc['sigma']:.1%}")
            st.write(f"Time: {sc['T']:.3f} years")
        
        with col2:
            st.markdown("#### After Event 1")
            st.write(f"Stock: ${first_event_data['spot']:.2f}")
            st.write(f"Vol: {first_event_data['vol']:.1%}")
            st.write(f"Time: {first_event_data['time']:.3f} years")
            st.write(f"P&L: ${first_event_pnl:+,.0f}")
        
        with col3:
            st.markdown("#### After Event 2")
            st.write(f"Stock: ${second_spot:.2f}")
            st.write(f"Vol: {second_vol:.1%}")
            st.write(f"Time: {second_time:.3f} years")
            st.write(f"P&L: ${second_event_pnl:+,.0f}")
        
        # Show total P&L
        total_pnl_status = "Profit" if cumulative_pnl > 0 else "Loss" if cumulative_pnl < 0 else "Breakeven"
        st.markdown(f"### **Total Position P&L: ${cumulative_pnl:+,.0f}** ({total_pnl_status})")
        
        # Final assessment form
        
                # Show final feedback
        st.markdown("### Final Results")
        
        if cumulative_pnl > 500:
            st.success(f"**Profitable Trading!** Total P&L: ${cumulative_pnl:+,.0f}")
        elif cumulative_pnl > -500:
            st.info(f"**Break-Even Trading** Total P&L: ${cumulative_pnl:+,.0f}")
        else:
            st.warning(f"**Learning Experience** Total P&L: ${cumulative_pnl:+,.0f}")
 
        # Option to start over
        if st.button("Start New Scenario", key="start_over_final"):
            for key in ['trading_stage', 'initial_position', 'market_events', 'event_response', 'final_assessment', 'step1_complete', 'step2_complete', 'step3_complete']:
                st.session_state.pop(key, None)
            st.rerun()

    # --- Final Summary Section ---
    if "final_assessment" in st.session_state:
        st.markdown("---")
        st.subheader("Trading Session Summary")
        
        assessment = st.session_state.final_assessment
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Session Statistics")
            st.write(f"**Final P&L**: ${assessment['total_pnl']:+,.0f}")
            st.write(f"**Events Handled**: {assessment['events_handled']}")
            st.write(f"**Performance Rating**: {assessment['performance']}")
            st.write(f"**Key Lesson**: {assessment['lesson']}")
        
        with col2:
            st.markdown("#### Areas for Improvement")
            if assessment['improvements']:
                st.write(assessment['improvements'])
            else:
                st.write("No specific improvements noted.")
        

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
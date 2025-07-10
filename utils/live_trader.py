"""Utilities for the live trading simulation."""

import streamlit as st
import numpy as np

from . import option_pricing as op
from . import greeks


class LiveTrader:
    """Encapsulates the multi-stage live trading simulation."""

    def __init__(self, scenario, call_delta, put_delta, call_theo, put_theo):
        """Store scenario parameters and initialize state."""
        self.scenario = scenario
        self.call_delta = call_delta
        self.put_delta = put_delta
        self.call_theo = call_theo
        self.put_theo = put_theo

        if "trading_stage" not in st.session_state:
            st.session_state.trading_stage = "initial"
        if "initial_position" not in st.session_state:
            st.session_state.initial_position = None
        if "market_events" not in st.session_state:
            st.session_state.market_events = []
        if "event_response" not in st.session_state:
            st.session_state.event_response = None

        self.stage = st.session_state.trading_stage
        self.initial_position = st.session_state.initial_position
        self.market_events = st.session_state.market_events
        self.event_response = st.session_state.event_response
        self.second_event_response = st.session_state.get("second_event_response")

        self.straddle_delta = self.call_delta + self.put_delta

    def render(self):
        """Render the interface for the current trading stage."""
        if self.stage == "initial":
            self._render_initial()
        elif self.stage == "market_event":
            self._render_event()
        elif self.stage == "feedback":
            self._render_feedback()
        elif self.stage == "second_event":
            self._render_second_event()

    def _advance_stage(self, next_stage):
        self.stage = next_stage
        st.session_state.trading_stage = next_stage
        st.experimental_rerun()

    # --- Stage Renderers ---

    def _render_initial(self):
        sc = self.scenario
        st.subheader("Initial Market Setup")
        st.info(
            f"""
        **Initial Market Conditions:**
        - Stock: ${sc['S']:.2f}
        - Call Market: ${sc['C_mkt']:.2f} | Theo: ${self.call_theo:.2f}
        - Put Market: ${sc['P_mkt']:.2f} | Theo: ${self.put_theo:.2f}
        - Time to expiry: {sc['T']:.2f} years
        - Volatility: {sc['sigma']:.1%}
        """
        )

        with st.form("initial_assessment"):
            st.markdown("### Quick Market Assessment")

            opportunity = st.selectbox(
                "What's the primary opportunity?",
                [
                    "Buy call",
                    "Sell call",
                    "Buy put",
                    "Sell put",
                    "Buy straddle",
                    "Sell straddle",
                    "No clear edge",
                ],
            )

            position_size = st.selectbox(
                "Position size?",
                ["1 contract", "2 contracts", "5 contracts", "10 contracts"],
            )

            hedge_decision = st.selectbox(
                "Delta hedge strategy?",
                [
                    "Hedge immediately",
                    "Hedge after 1% move",
                    "Stay unhedged",
                    "Partial hedge",
                ],
            )

            if st.form_submit_button("Enter Initial Position"):
                st.session_state.initial_position = {
                    "trade": opportunity,
                    "size": int(position_size.split()[0]),
                    "hedge_strategy": hedge_decision,
                    "entry_spot": sc["S"],
                    "entry_time": sc["T"],
                }

                pos_delta = 0
                if "call" in opportunity:
                    pos_delta = self.call_delta * (1 if "buy" in opportunity.lower() else -1)
                    pos_delta *= st.session_state.initial_position["size"]
                elif "put" in opportunity:
                    pos_delta = self.put_delta * (1 if "buy" in opportunity.lower() else -1)
                    pos_delta *= st.session_state.initial_position["size"]
                elif "straddle" in opportunity:
                    pos_delta = self.straddle_delta * (1 if "buy" in opportunity.lower() else -1)
                    pos_delta *= st.session_state.initial_position["size"]

                st.session_state.initial_position["delta"] = pos_delta
                self._advance_stage("market_event")

    def _render_event(self):
        sc = self.scenario
        st.subheader("Market Event!")

        if not st.session_state.get("market_events"):
            import random

            events = [
                {
                    "type": "stock_move",
                    "description": "Stock gaps up 3% on earnings beat",
                    "new_spot": sc["S"] * 1.03,
                    "vol_change": -0.05,
                    "time_passed": 0.01,
                },
                {
                    "type": "vol_spike",
                    "description": "Market volatility spikes due to Fed announcement",
                    "new_spot": sc["S"] * 0.995,
                    "vol_change": 0.15,
                    "time_passed": 0.005,
                },
                {
                    "type": "time_decay",
                    "description": "Two weeks pass with sideways action",
                    "new_spot": sc["S"] * random.uniform(0.98, 1.02),
                    "vol_change": -0.03,
                    "time_passed": 0.04,
                },
                {
                    "type": "gap_down",
                    "description": "Stock gaps down 2.5% on sector news",
                    "new_spot": sc["S"] * 0.975,
                    "vol_change": 0.08,
                    "time_passed": 0.01,
                },
            ]

            st.session_state.market_events = [random.choice(events)]

        event = st.session_state.market_events[0]

        st.warning(f"**MARKET EVENT**: {event['description']}")

        new_spot = event["new_spot"]
        new_vol = max(0.1, sc["sigma"] + event["vol_change"])
        new_time = max(0.01, sc["T"] - event["time_passed"])

        new_call_theo = op.call_price(new_spot, sc["K"], sc["r"], new_time, new_vol)
        new_put_theo = op.put_price(new_spot, sc["K"], sc["r"], new_time, new_vol)
        new_call_delta = greeks.call_delta(new_spot, sc["K"], sc["r"], new_time, new_vol)
        new_put_delta = greeks.put_delta(new_spot, sc["K"], sc["r"], new_time, new_vol)

        def calculate_pnl():
            pos = st.session_state.initial_position
            pnl = 0
            if "buy call" in pos["trade"]:
                pnl = (new_call_theo - self.call_theo) * pos["size"] * 100
            elif "sell call" in pos["trade"]:
                pnl = (self.call_theo - new_call_theo) * pos["size"] * 100
            elif "buy put" in pos["trade"]:
                pnl = (new_put_theo - self.put_theo) * pos["size"] * 100
            elif "sell put" in pos["trade"]:
                pnl = (self.put_theo - new_put_theo) * pos["size"] * 100
            elif "buy straddle" in pos["trade"]:
                pnl = ((new_call_theo - self.call_theo) + (new_put_theo - self.put_theo)) * pos["size"] * 100
            elif "sell straddle" in pos["trade"]:
                pnl = ((self.call_theo - new_call_theo) + (self.put_theo - new_put_theo)) * pos["size"] * 100
            return pnl

        current_pnl = calculate_pnl()

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Before Event")
            st.write(f"Stock: ${sc['S']:.2f}")
            st.write(f"Vol: {sc['sigma']:.1%}")
            st.write(f"Time: {sc['T']:.3f} years")
            st.write(f"Call Theo: ${self.call_theo:.2f}")
            st.write(f"Put Theo: ${self.put_theo:.2f}")

        with col2:
            st.markdown("#### After Event")
            st.write(f"Stock: ${new_spot:.2f} ({((new_spot/sc['S'])-1)*100:+.1f}%)")
            st.write(f"Vol: {new_vol:.1%} ({(new_vol-sc['sigma'])*100:+.1f}%)")
            st.write(f"Time: {new_time:.3f} years")
            st.write(f"Call Theo: ${new_call_theo:.2f}")
            st.write(f"Put Theo: ${new_put_theo:.2f}")

        pnl_status = "Profit" if current_pnl > 0 else "Loss" if current_pnl < 0 else "Breakeven"
        st.markdown(f"### Position P&L: ${current_pnl:+,.0f} ({pnl_status})")

        with st.form("event_response_form"):
            st.markdown("### How Do You Respond?")
            risk_level = st.selectbox(
                "1. How would you rate your current risk level?",
                [
                    "Low risk - hold position",
                    "Medium risk - monitor closely",
                    "High risk - need to adjust",
                    "Extreme risk - close immediately",
                ],
            )
            new_delta_guess = st.number_input(
                "2. What's your new position delta approximately?",
                format="%.2f",
            )
            action = st.selectbox(
                "3. What action will you take?",
                [
                    "Hold position unchanged",
                    "Add to position",
                    "Reduce position size",
                    "Close position",
                    "Hedge with stock",
                    "Roll to different strike",
                    "Add hedging options",
                ],
            )
            if action in ["Hedge with stock", "Add hedging options"]:
                hedge_amount = st.number_input(
                    "How much hedge? (shares if stock, contracts if options)",
                    format="%.0f",
                )
            else:
                hedge_amount = 0
            urgency = st.selectbox(
                "4. How urgent is this action?",
                [
                    "Execute immediately",
                    "Wait for better pricing",
                    "End of day is fine",
                    "Monitor and decide later",
                ],
            )

            if st.form_submit_button("Execute Response"):
                st.session_state.event_response = {
                    "risk_assessment": risk_level,
                    "delta_guess": new_delta_guess,
                    "action": action,
                    "hedge_amount": hedge_amount,
                    "urgency": urgency,
                    "correct_delta": new_call_delta,
                    "actual_pnl": current_pnl,
                    "new_market_data": {
                        "spot": new_spot,
                        "vol": new_vol,
                        "time": new_time,
                        "call_theo": new_call_theo,
                        "put_theo": new_put_theo,
                    },
                }
                self._advance_stage("feedback")

    def _render_feedback(self):
        st.subheader("Response Analysis")
        response = st.session_state.event_response

        st.markdown("### Scorecard")
        score = 0
        total_points = 5
        actual_pnl = response["actual_pnl"]

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

        delta_error = abs(response["delta_guess"] - response["correct_delta"])
        if delta_error <= abs(response["correct_delta"]) * 0.2:
            st.write(
                f"Delta estimate: within acceptable range (actual {response['correct_delta']:.2f})."
            )
            score += 1
        else:
            st.write(
                f"Delta estimate: off by {delta_error:.2f}. Actual: {response['correct_delta']:.2f}."
            )

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

        if action == "Hedge with stock":
            ideal_hedge = abs(response["correct_delta"]) * 100
            hedge_amt = response["hedge_amount"]
            if abs(hedge_amt - ideal_hedge) <= ideal_hedge * 0.3:
                st.write("Hedge sizing: appropriate.")
                score += 1
            else:
                st.write(f"Hedge sizing: expected ~{ideal_hedge:.0f}, got {hedge_amt:.0f}.")
        else:
            score += 1

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

        percentage = (score / total_points) * 100
        st.markdown(f"**Final Score:** {score:.1f}/{total_points} ({percentage:.0f}%)")

        st.markdown("### Additional Insights")
        event_type = st.session_state.market_events[0]["type"]
        insights = {
            "stock_move": "- Watch gamma: large moves shift delta significantly.\n- Volatility often drops after earnings.",
            "vol_spike": "- Long options gain, short options lose.\n- Hedging costs rise with higher vol.",
            "time_decay": "- Theta accelerates near expiration.\n- Shorts benefit from time decay.",
            "gap_down": "- Sudden moves spike vega P&L.\n- Determine if move is sector-specific or market-wide.",
        }
        st.write(insights.get(event_type, "Review your decision in context of the market event."))

        col1, col2 = st.columns(2)
        if col1.button("Next Event"):
            self._advance_stage("second_event")
        if col2.button("Start New Scenario"):
            for key in [
                "trading_stage",
                "initial_position",
                "market_events",
                "event_response",
                "step1_complete",
                "step2_complete",
                "step3_complete",
            ]:
                st.session_state.pop(key, None)
            st.experimental_rerun()

    def _render_second_event(self):
        sc = self.scenario
        st.subheader("Second Market Event!")

        follow_up_events = [
            {
                "type": "volatility_collapse",
                "description": "Vol crush: Market calms down, volatility drops 40%",
                "vol_multiplier": 0.6,
                "spot_change": 1.005,
                "time_passed": 0.02,
            },
            {
                "type": "whipsaw",
                "description": "Market whipsaws: Stock reverses previous move",
                "vol_multiplier": 1.2,
                "spot_change": 0.985 if st.session_state.market_events[0]["new_spot"] > sc["S"] else 1.015,
                "time_passed": 0.01,
            },
            {
                "type": "acceleration",
                "description": "Trend accelerates: Move continues in same direction",
                "vol_multiplier": 1.1,
                "spot_change": 1.02 if st.session_state.market_events[0]["new_spot"] > sc["S"] else 0.98,
                "time_passed": 0.015,
            },
        ]

        import random

        second_event = random.choice(follow_up_events)
        st.warning(f"**SECOND EVENT**: {second_event['description']}")

        first_event_data = st.session_state.event_response["new_market_data"]
        second_spot = first_event_data["spot"] * second_event["spot_change"]
        second_vol = max(0.1, first_event_data["vol"] * second_event["vol_multiplier"])
        second_time = max(0.005, first_event_data["time"] - second_event["time_passed"])

        second_call_theo = op.call_price(second_spot, sc["K"], sc["r"], second_time, second_vol)
        second_put_theo = op.put_price(second_spot, sc["K"], sc["r"], second_time, second_vol)
        second_call_delta = greeks.call_delta(second_spot, sc["K"], sc["r"], second_time, second_vol)
        second_put_delta = greeks.put_delta(second_spot, sc["K"], sc["r"], second_time, second_vol)

        def calculate_cumulative_pnl():
            pos = st.session_state.initial_position
            pnl = 0
            if "buy call" in pos["trade"]:
                pnl = (second_call_theo - self.call_theo) * pos["size"] * 100
            elif "sell call" in pos["trade"]:
                pnl = (self.call_theo - second_call_theo) * pos["size"] * 100
            elif "buy put" in pos["trade"]:
                pnl = (second_put_theo - self.put_theo) * pos["size"] * 100
            elif "sell put" in pos["trade"]:
                pnl = (self.put_theo - second_put_theo) * pos["size"] * 100
            elif "buy straddle" in pos["trade"]:
                pnl = ((second_call_theo - self.call_theo) + (second_put_theo - self.put_theo)) * pos["size"] * 100
            elif "sell straddle" in pos["trade"]:
                pnl = ((self.call_theo - second_call_theo) + (self.put_theo - second_put_theo)) * pos["size"] * 100
            return pnl

        cumulative_pnl = calculate_cumulative_pnl()
        first_event_pnl = st.session_state.event_response["actual_pnl"]
        second_event_pnl = cumulative_pnl - first_event_pnl

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

        total_pnl_status = "Profit" if cumulative_pnl > 0 else "Loss" if cumulative_pnl < 0 else "Breakeven"
        st.markdown(f"### **Total Position P&L: ${cumulative_pnl:+,.0f}** ({total_pnl_status})")

        st.markdown("### Final Results")
        if cumulative_pnl > 500:
            st.success(f"**Profitable Trading!** Total P&L: ${cumulative_pnl:+,.0f}")
        elif cumulative_pnl > -500:
            st.info(f"**Break-Even Trading** Total P&L: ${cumulative_pnl:+,.0f}")
        else:
            st.warning(f"**Learning Experience** Total P&L: ${cumulative_pnl:+,.0f}")

        if st.button("Start New Scenario", key="start_over_final"):
            for key in [
                "trading_stage",
                "initial_position",
                "market_events",
                "event_response",
                "final_assessment",
                "step1_complete",
                "step2_complete",
                "step3_complete",
            ]:
                st.session_state.pop(key, None)
            st.experimental_rerun()


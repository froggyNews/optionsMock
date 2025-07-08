import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from option_pricing import call_price, put_price
import parity
import delta_hedging as dh
import quiz


def setup_page_config():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="Options Practice App",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )


def initialize_session_state():
    """Initialize session state variables"""
    if "pcp_params" not in st.session_state:
        st.session_state.pcp_params = None
    if "dh_state" not in st.session_state:
        st.session_state.dh_state = None
    if "dh_history" not in st.session_state:
        st.session_state.dh_history = []
    if "quiz" not in st.session_state:
        st.session_state.quiz = None
    if "show_answer" not in st.session_state:
        st.session_state.show_answer = False


def put_call_parity_page():
    """Enhanced Put-Call Parity page"""
    st.header("Put-Call Parity Practice")
    
    # Add explanation
    with st.expander("📚 Put-Call Parity Explanation"):
        st.latex(r"C - P = S - K \cdot e^{-r \cdot T}")
        st.write("""
        - **C**: Call option price
        - **P**: Put option price  
        - **S**: Current stock price
        - **K**: Strike price
        - **r**: Risk-free rate
        - **T**: Time to expiration
        """)
    
    # Generate parameters section
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("🎲 Generate New Parameters", type="primary"):
            st.session_state.pcp_params = parity.generate_parameters()
            st.session_state.show_answer = False
    
    with col2:
        if st.button("🔄 Reset"):
            st.session_state.pcp_params = None
            st.session_state.show_answer = False
    
    # Display parameters if they exist
    if st.session_state.pcp_params is None:
        st.info("Click 'Generate New Parameters' to start practicing!")
        return
    
    params = st.session_state.pcp_params
    
    # Display parameters in a nice format
    st.subheader("📊 Market Parameters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Stock Price (S)", f"${params['S']:.2f}")
        st.metric("Strike Price (K)", f"${params['K']:.2f}")
    
    with col2:
        st.metric("Call Price (C)", f"${params['C']:.2f}")
        st.metric("Put Price (P)", f"${params['P']:.2f}")
    
    with col3:
        st.metric("Risk-free Rate (r)", f"{params['r']:.3f}")
        st.metric("Time to Expiration (T)", f"{params['T']:.2f} years")
    
    # User input section
    st.subheader("🤔 Your Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        violation_user = st.radio(
            "Is put-call parity violated?", 
            ("Yes", "No"),
            key="parity_violation"
        )
    
    with col2:
        trade_user = st.radio(
            "What arbitrage trade should you make?",
            (
                "Buy call, sell put, buy stock, borrow PV(K)",
                "Sell call, buy put, short stock, lend PV(K)",
                "No trade needed",
            ),
            key="arbitrage_trade"
        )
    
    # Check answer button
    if st.button("✅ Check Answer", type="secondary"):
        st.session_state.show_answer = True
    
    # Show answer if requested
    if st.session_state.show_answer:
        violated, diff = parity.parity_violation(params)
        arb = parity.arbitrage_strategy(diff)
        
        # Check if user is correct
        violation_correct = (
            (violated and violation_user == "Yes") or 
            (not violated and violation_user == "No")
        )
        trade_correct = trade_user == arb
        overall_correct = violation_correct and trade_correct
        
        # Display results
        st.subheader("📝 Results")
        
        if overall_correct:
            st.success("🎉 Correct! Well done!")
        else:
            st.error("❌ Incorrect. Let's see what went wrong:")
        
        # Detailed breakdown
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Parity Violation Analysis:**")
            if violation_correct:
                st.success(f"✅ Correct: Parity {'is' if violated else 'is not'} violated")
            else:
                st.error(f"❌ Incorrect: Parity {'is' if violated else 'is not'} violated")
            
            st.write(f"**Difference:** {diff:.4f}")
            if abs(diff) > 1e-2:
                st.write("Since |difference| > 0.01, parity is violated")
            else:
                st.write("Since |difference| ≤ 0.01, parity holds")
        
        with col2:
            st.write("**Arbitrage Strategy:**")
            if trade_correct:
                st.success(f"✅ Correct strategy: {arb}")
            else:
                st.error(f"❌ Incorrect. Correct strategy: {arb}")
        
        # Show payoff diagram
        st.subheader("📈 Payoff Diagram")
        fig = parity.payoff_diagram(params, diff)
        st.pyplot(fig)


def delta_hedging_page():
    """Enhanced Delta Hedging page"""
    st.header("Delta Hedging Simulation")
    
    # Add explanation
    with st.expander("📚 Delta Hedging Explanation"):
        st.write("""
        Delta hedging involves maintaining a delta-neutral portfolio by continuously 
        adjusting your position in the underlying stock. The goal is to minimize 
        the portfolio's sensitivity to small changes in the stock price.
        """)
    
    # Parameters section
    st.subheader("⚙️ Simulation Parameters")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        S0 = st.number_input("Initial Stock Price", value=100.0, step=1.0)
    with col2:
        K = st.number_input("Strike Price", value=100.0, step=1.0)
    with col3:
        r = st.number_input("Risk-free Rate", value=0.01, step=0.001, format="%.3f")
    with col4:
        T = st.number_input("Time to Expiration", value=1.0, step=0.1)
    
    dt = 1 / 52  # Weekly steps
    
    # Initialize state if needed
    if (st.session_state.dh_state is None or 
        st.button("🔄 Reset Simulation", type="secondary")):
        st.session_state.dh_state = dh.init_state(S0, K, r, T)
        st.session_state.dh_history = []
    
    # Current state display
    state = st.session_state.dh_state
    
    st.subheader("📊 Current State")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Stock Price", f"${state['S']:.2f}")
    with col2:
        st.metric("Option Price", f"${state['option_price']:.2f}")
    with col3:
        st.metric("Delta", f"{state['delta']:.4f}")
    with col4:
        st.metric("Time Remaining", f"{state['t']:.3f} years")
    
    # Hedging controls
    st.subheader("🎯 Hedging Control")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        hedge_ratio = st.slider(
            "Hedge Ratio (shares of stock)", 
            -2.0, 2.0, 0.0, step=0.1,
            help="Number of shares to hold. Negative means short position."
        )
    
    with col2:
        if st.button("➡️ Next Step", type="primary"):
            new_state = dh.update_state(
                st.session_state.dh_state, hedge_ratio, K, r, T, dt
            )
            # Store history
            st.session_state.dh_history.append({
                'time': state['t'],
                'stock_price': state['S'],
                'option_price': state['option_price'],
                'delta': state['delta'],
                'hedge_ratio': hedge_ratio,
                'cash': state['cash']
            })
            st.session_state.dh_state = new_state
    
    with col3:
        st.write(f"**Suggested Delta:** {state['delta']:.4f}")
        st.write(f"**Your Hedge:** {hedge_ratio:.1f}")
        if abs(hedge_ratio - state['delta']) < 0.1:
            st.success("✅ Good hedge!")
        else:
            st.warning("⚠️ Consider adjusting")
    
    # Show history if available
    if st.session_state.dh_history:
        st.subheader("📈 Simulation History")
        
        history_df = pd.DataFrame(st.session_state.dh_history)
        
        # Create charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Stock Price Over Time**")
            st.line_chart(history_df.set_index('time')['stock_price'])
        
        with col2:
            st.write("**Delta Over Time**")
            st.line_chart(history_df.set_index('time')['delta'])
        
        # Show data table
        if st.checkbox("Show detailed history"):
            st.dataframe(history_df)


def quiz_page():
    """Enhanced Quiz page"""
    st.header("Options Knowledge Quiz")
    
    # Load and display score
    score, total = quiz.load_history()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Score", f"{score}/{total}")
    with col2:
        if total > 0:
            st.metric("Percentage", f"{(score/total)*100:.1f}%")
        else:
            st.metric("Percentage", "0%")
    with col3:
        if st.button("📊 View History"):
            # Could add a more detailed history view here
            st.info("Detailed history feature coming soon!")
    
    # Initialize quiz question if needed
    if st.session_state.quiz is None:
        q, opts, ans, idx = quiz.ask_question()
        st.session_state.quiz = {"q": q, "opts": opts, "ans": ans, "idx": idx}
        st.session_state.answered = False
    
    qdata = st.session_state.quiz
    
    # Display question
    st.subheader("❓ Question")
    st.write(qdata["q"])
    
    # Answer options
    if not st.session_state.get("answered", False):
        choice = st.radio("Select your answer:", qdata["opts"], key="quiz_choice")
        
        if st.button("Submit Answer", type="primary"):
            correct = qdata["opts"].index(choice) == qdata["ans"]
            quiz.record_result(correct)
            
            # Show result
            if correct:
                st.success("🎉 Correct!")
            else:
                st.error(f"❌ Incorrect. The correct answer was: {qdata['opts'][qdata['ans']]}")
            
            st.session_state.answered = True
    
    # Show next question button after answering
    if st.session_state.get("answered", False):
        if st.button("Next Question", type="secondary"):
            q, opts, ans, idx = quiz.ask_question()
            st.session_state.quiz = {"q": q, "opts": opts, "ans": ans, "idx": idx}
            st.session_state.answered = False
            st.rerun()


def main():
    """Main application function"""
    setup_page_config()
    initialize_session_state()
    
    # Title and navigation
    st.title("📈 Options Practice App")
    st.markdown("---")
    
    # Sidebar navigation
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Mode",
            ("Put-Call Parity", "Delta Hedging", "Quiz"),
            index=0
        )
        
        st.markdown("---")
        st.subheader("About")
        st.write("Practice options trading concepts with interactive simulations and quizzes.")
        
        st.markdown("---")
        st.subheader("Quick Tips")
        if page == "Put-Call Parity":
            st.write("• Look for pricing discrepancies")
            st.write("• Consider arbitrage opportunities")
            st.write("• Remember: C - P = S - K⋅e^(-rT)")
        elif page == "Delta Hedging":
            st.write("• Match hedge ratio to delta")
            st.write("• Monitor portfolio sensitivity")
            st.write("• Adjust frequently for best results")
        elif page == "Quiz":
            st.write("• Test your knowledge")
            st.write("• Track your progress")
            st.write("• Learn from mistakes")
    
    # Route to appropriate page
    if page == "Put-Call Parity":
        put_call_parity_page()
    elif page == "Delta Hedging":
        delta_hedging_page()
    elif page == "Quiz":
        quiz_page()


if __name__ == "__main__":
    main()

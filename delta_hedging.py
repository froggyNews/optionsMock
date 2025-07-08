import numpy as np
from option_pricing import call_price, call_delta


ndefault_sigma = 0.2

def simulate_step(S_prev, r, sigma, dt):
    """Simulate next stock price using geometric Brownian motion"""
    dW = np.random.normal(scale=np.sqrt(dt))
    return S_prev * np.exp((r - 0.5 * sigma ** 2) * dt + sigma * dW)


def init_state(S0, K, r, T, sigma=ndefault_sigma):
    price = call_price(S0, K, r, T, sigma)
    delta = call_delta(S0, K, r, T, sigma)
    return {
        "S": S0,
        "t": 0.0,
        "cash": price,  # premium received from selling the call
        "delta": delta,
        "option_price": price,
    }


def update_state(state, hedge_ratio, K, r, T, dt, sigma=ndefault_sigma):
    S_new = simulate_step(state["S"], r, sigma, dt)
    t_new = state["t"] + dt
    option_new = call_price(S_new, K, r, T - t_new, sigma)
    delta_new = call_delta(S_new, K, r, T - t_new, sigma)

    # Hedge P&L from holding shares
    hedge_pnl = hedge_ratio * (S_new - state["S"])

    # Option P&L (short position)
    option_pnl = -(option_new - state["option_price"])

    cash_new = state["cash"] + hedge_pnl + option_pnl

    state.update({
        "S": S_new,
        "t": t_new,
        "cash": cash_new,
        "option_price": option_new,
        "delta": delta_new,
    })
    return state

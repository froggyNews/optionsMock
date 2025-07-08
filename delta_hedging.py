"""Utility functions for a simple delta hedging simulation."""

import numpy as np
import matplotlib.pyplot as plt
from option_pricing import call_price, call_delta


ndefault_sigma = 0.2

def simulate_step(S_prev, r, sigma, dt):
    """Simulate next stock price using geometric Brownian motion"""
    dW = np.random.normal(scale=np.sqrt(dt))
    return S_prev * np.exp((r - 0.5 * sigma ** 2) * dt + sigma * dW)


def init_state(S0, K, r, T, sigma=ndefault_sigma):
    """Return initial simulation state with history trackers."""
    price = call_price(S0, K, r, T, sigma)
    delta = call_delta(S0, K, r, T, sigma)
    state = {
        "S": S0,
        "t": 0.0,
        "cash": price,  # premium from selling the call
        "pnl": 0.0,
        "delta": delta,
        "hedge": 0.0,
        "option_price": price,
        "history": {
            "t": [0.0],
            "S": [S0],
            "delta": [delta],
            "hedge": [0.0],
            "pnl": [0.0],
        },
    }
    return state


def update_state(state, hedge_ratio, K, r, T, dt, sigma=ndefault_sigma, auto_hedge=False):
    """Advance simulation by one time step.

    Parameters
    ----------
    state : dict
        Current simulation state.
    hedge_ratio : float
        Number of shares held during the step. Ignored if ``auto_hedge`` is
        ``True``.
    auto_hedge : bool, optional
        If ``True``, set hedge ratio to ``-delta`` at the start of the step.
    """

    if auto_hedge:
        hedge_ratio = -state["delta"]

    S_new = simulate_step(state["S"], r, sigma, dt)
    t_new = state["t"] + dt
    option_new = call_price(S_new, K, r, T - t_new, sigma)
    delta_new = call_delta(S_new, K, r, T - t_new, sigma)

    # P&L from existing hedge position
    hedge_pnl = hedge_ratio * (S_new - state["S"])
    # Short option P&L
    option_pnl = -(option_new - state["option_price"])

    pnl_new = state["pnl"] + hedge_pnl + option_pnl
    cash_new = state["cash"] + hedge_pnl + option_pnl

    state.update({
        "S": S_new,
        "t": t_new,
        "cash": cash_new,
        "pnl": pnl_new,
        "option_price": option_new,
        "delta": delta_new,
        "hedge": hedge_ratio,
    })

    hist = state["history"]
    for key, value in {
        "t": t_new,
        "S": S_new,
        "delta": delta_new,
        "hedge": hedge_ratio,
        "pnl": pnl_new,
    }.items():
        hist[key].append(value)

    return state


def plot_history(state):
    """Return a matplotlib figure of price, hedge and P&L evolution."""
    hist = state["history"]
    t = hist["t"]

    fig, axes = plt.subplots(2, 1, figsize=(6, 5), sharex=True)

    axes[0].plot(t, hist["S"], label="Stock")
    axes[0].set_ylabel("Stock Price")
    ax2 = axes[0].twinx()
    ax2.plot(t, hist["delta"], color="tab:orange", label="Option Delta")
    ax2.plot(t, hist["hedge"], color="tab:green", linestyle="--", label="Hedge")
    ax2.set_ylabel("Delta / Hedge")

    lines, labels = axes[0].get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    axes[0].legend(lines + lines2, labels + labels2, loc="best")

    axes[1].plot(t, hist["pnl"], color="tab:purple", label="P&L")
    axes[1].set_ylabel("P&L")
    axes[1].set_xlabel("Time")
    axes[1].legend(loc="best")

    fig.tight_layout()
    return fig

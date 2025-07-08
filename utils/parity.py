import numpy as np
import matplotlib.pyplot as plt
from .option_pricing import call_price, put_price


def generate_parameters():
    S = np.random.uniform(80, 120)
    K = round(np.random.uniform(80, 120) * 2) / 2

    r = np.random.uniform(0.0, 0.05)
    T = np.random.uniform(0.25, 1.0)  # in years
    sigma = 0.2

    C = call_price(S, K, r, T, sigma)
    P = put_price(S, K, r, T, sigma)

    # Introduce small random noise to potentially create parity violation
    noise = np.random.normal(scale=0.5)
    if np.random.rand() > 0.5:
        C += noise
    else:
        P += noise

    params = {"S": S, "K": K, "C": C, "P": P, "r": r, "T": T, "sigma": sigma}

    return params


def parity_violation(params, tol=1e-2):
    lhs = params["C"] - params["P"]
    rhs = params["S"] - params["K"] * np.exp(-params["r"] * params["T"])
    diff = lhs - rhs
    return abs(diff) > tol, diff


def arbitrage_strategy(diff):
    if diff > 0:
        return "Sell call, buy put, short stock, lend PV(K)"
    elif diff < 0:
        return "Buy call, sell put, buy stock, borrow PV(K)"
    else:
        return "No arbitrage"


def payoff_diagram(params, diff):
    S_vals = np.linspace(0.5 * params["K"], 1.5 * params["K"], 100)
    if diff > 0:
        payoff = (
            -call_price(S_vals, params["K"], params["r"], params["T"], 0.2)
            + put_price(S_vals, params["K"], params["r"], params["T"], 0.2)
            - S_vals
            + params["K"] * np.exp(-params["r"] * params["T"])
        )
    else:
        payoff = (
            call_price(S_vals, params["K"], params["r"], params["T"], 0.2)
            - put_price(S_vals, params["K"], params["r"], params["T"], 0.2)
            + S_vals
            - params["K"] * np.exp(-params["r"] * params["T"])
        )
    fig, ax = plt.subplots()
    ax.plot(S_vals, payoff)
    ax.axhline(0, color="k", linestyle="--")
    ax.set_xlabel("Stock Price at Expiration")
    ax.set_ylabel("Arbitrage Payoff")
    return fig

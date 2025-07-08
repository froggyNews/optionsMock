import numpy as np

from .option_pricing import call_price, put_price


def generate_scenario():
    """Return random option scenario with theoretical and market prices."""
    S = np.round(np.random.uniform(50, 150), 2)
    K = np.round(np.random.uniform(50, 150) / 0.5) * 0.5
    T = np.round(np.random.uniform(0.1, 1.0), 2)
    r = np.round(np.random.uniform(0.01, 0.05), 4)
    sigma = np.round(np.random.uniform(0.1, 0.7), 2)

    C_theo = call_price(S, K, r, T, sigma)
    P_theo = put_price(S, K, r, T, sigma)

    # Add small noise to create market prices
    C_mkt = C_theo + np.random.normal(scale=0.25)
    P_mkt = P_theo + np.random.normal(scale=0.25)

    pvk = K * np.exp(-r * T)
    parity = S - pvk
    diff = C_mkt - P_mkt - parity

    if diff > 0:
        arb = "Sell call, buy put, short stock, lend PV(K)"
    elif diff < 0:
        arb = "Buy call, sell put, buy stock, borrow PV(K)"
    else:
        arb = "No arbitrage"

    return {
        "S": S,
        "K": K,
        "T": T,
        "r": r,
        "sigma": sigma,
        "C_theo": C_theo,
        "P_theo": P_theo,
        "C_mkt": C_mkt,
        "P_mkt": P_mkt,
        "pvk": pvk,
        "parity_diff": diff,
        "arb": arb,
    }

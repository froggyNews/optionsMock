import numpy as np
from .option_pricing import (
    call_delta,
    put_delta,
    gamma,
    vega,
    call_theta,
    put_theta,
    call_rho,
    put_rho,
)


GREEK_KEYS = ["delta", "gamma", "vega", "theta", "rho"]


def compute_greeks(S, K, r, T, sigma, option_type="call"):
    """Return dictionary of option Greeks."""
    if option_type == "call":
        return {
            "delta": call_delta(S, K, r, T, sigma),
            "gamma": gamma(S, K, r, T, sigma),
            "vega": vega(S, K, r, T, sigma),
            "theta": call_theta(S, K, r, T, sigma),
            "rho": call_rho(S, K, r, T, sigma),
        }
    else:
        return {
            "delta": put_delta(S, K, r, T, sigma),
            "gamma": gamma(S, K, r, T, sigma),
            "vega": vega(S, K, r, T, sigma),
            "theta": put_theta(S, K, r, T, sigma),
            "rho": put_rho(S, K, r, T, sigma),
        }


def net_position_greeks(trade, S, K, r, T, sigma):
    """Sum Greeks for a trade dictionary."""
    call_g = compute_greeks(S, K, r, T, sigma, "call")
    put_g = compute_greeks(S, K, r, T, sigma, "put")
    # stock Greeks
    stock = {"delta": 1.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0, "rho": 0.0}
    bond = {"delta": 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0, "rho": -K * T * np.exp(-r * T) / 100}

    total = {k: 0.0 for k in GREEK_KEYS}
    for g in GREEK_KEYS:
        total[g] += trade.get("call", 0) * call_g[g]
        total[g] += trade.get("put", 0) * put_g[g]
        total[g] += trade.get("stock", 0) * stock[g]
        total[g] += trade.get("pvk", 0) * bond[g]
    return total

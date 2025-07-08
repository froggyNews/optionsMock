import numpy as np
import pandas as pd

from .option_pricing import (
    call_price,
    put_price,
    call_delta,
    put_delta,
    gamma,
    vega,
    call_rho,
    put_rho,
)


def generate_chain(S, r, expiries, strikes, sigma):
    """Return DataFrame of option metrics for given parameters."""
    rows = []
    for T in expiries:
        for K in strikes:
            c_price = call_price(S, K, r, T, sigma)
            p_price = put_price(S, K, r, T, sigma)
            c_delta = call_delta(S, K, r, T, sigma)
            p_delta = put_delta(S, K, r, T, sigma)
            g = gamma(S, K, r, T, sigma)
            v = vega(S, K, r, T, sigma)
            c_rho = call_rho(S, K, r, T, sigma)
            p_rho = put_rho(S, K, r, T, sigma)
            revcon = c_price - p_price - S + K * np.exp(-r * T)
            rows.append({
                "Expiry": T,
                "Strike": K,
                "Call Delta": c_delta,
                "Call Price": c_price,
                "Put Price": p_price,
                "Put Delta": p_delta,
                "IV": sigma,
                "Vega": v,
                "Gamma": g,
                "RevCon": revcon,
                "cRho": c_rho,
                "pRho": p_rho,
            })
    return pd.DataFrame(rows)


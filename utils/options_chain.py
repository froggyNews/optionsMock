import numpy as np
import pandas as pd
from datetime import datetime
from pandas.tseries.offsets import DateOffset

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


def _expiry_label(months: int) -> str:
    """Return month name label for given months offset."""
    date = datetime.now() + DateOffset(months=months)
    return date.strftime("%b")


def generate_chain(S, r, expiries, strikes, sigma):
    """Return formatted DataFrame of option metrics."""
    rows = []
    for T in expiries:
        label = _expiry_label(int(round(T * 12)))
        for K in strikes:
            K_fmt = round(K * 2) / 2  # .0 or .5 increments
            c_price = call_price(S, K_fmt, r, T, sigma)
            p_price = put_price(S, K_fmt, r, T, sigma)
            c_delta = int(round(call_delta(S, K_fmt, r, T, sigma) * 100))
            p_delta = int(round(put_delta(S, K_fmt, r, T, sigma) * 100))
            g = gamma(S, K_fmt, r, T, sigma)
            v = vega(S, K_fmt, r, T, sigma)
            c_rho = call_rho(S, K_fmt, r, T, sigma)
            p_rho = put_rho(S, K_fmt, r, T, sigma)
            revcon = c_price - p_price - S + K_fmt * np.exp(-r * T)
            rows.append(
                {
                    "Expiry": label,
                    "Strike": K_fmt,
                    "Call Price": c_price,
                    "Put Price": p_price,
                    "Call Delta": c_delta,
                    "Put Delta": p_delta,
                    "Gamma": g,
                    "Vega": v,
                    "Call Rho": c_rho,
                    "Put Rho": p_rho,
                    "RevCon": revcon,
                    "IV": f"{sigma * 100:.2f}%",
                }
            )

    df = pd.DataFrame(rows)
    groups = []
    for exp, group in df.groupby("Expiry", sort=False):
        groups.append(group.reset_index(drop=True))
        groups.append(pd.DataFrame([{}]))  # blank line
    df_formatted = pd.concat(groups, ignore_index=True)
    return df_formatted[df.columns]


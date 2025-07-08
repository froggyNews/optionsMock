import numpy as np
import pandas as pd

from trade_simulation import (
    TRADE_MAP,
    trade_from_choices,
    simulate_trade,
    pv_k,
)


def action_name(leg: str, sign: int) -> str:
    """Return human readable action name for a trade leg."""
    if leg in {"call", "put"}:
        mapping = {1: "Buy", -1: "Sell", 0: "None"}
    elif leg == "stock":
        mapping = {1: "Long", -1: "Short", 0: "None"}
    else:  # pvk
        mapping = {1: "Borrow", -1: "Lend", 0: "None"}
    return mapping.get(sign, "None")


def trade_summary_table(params: dict, trade: dict) -> pd.DataFrame:
    """Return a DataFrame summarizing the trade legs and prices."""
    prices = {
        "call": params["C"],
        "put": params["P"],
        "stock": params["S"],
        "pvk": pv_k(params["K"], params["r"], params["T"]),
    }
    rows = []
    for leg in ["call", "put", "stock", "pvk"]:
        rows.append(
            {
                "Leg": "PV(K)" if leg == "pvk" else leg.capitalize(),
                "Action": action_name(leg, trade.get(leg, 0)),
                "Price": round(prices[leg], 2),
            }
        )
    return pd.DataFrame(rows)


def compare_trades(user_trade: dict, correct_trade: dict):
    """Return number of matching legs and list of mismatched legs."""
    matches = [leg for leg in user_trade if user_trade[leg] == correct_trade.get(leg, 0)]
    mismatched = [leg for leg in user_trade if user_trade[leg] != correct_trade.get(leg, 0)]
    return len(matches), mismatched


def hint_message(mismatched):
    """Construct a hint string from mismatched legs."""
    if not mismatched:
        return None
    names = ["PV(K)" if leg == "pvk" else leg.capitalize() for leg in mismatched]
    return "Consider adjusting: " + ", ".join(names)


def payoff_simulation(params: dict, trade: dict, spots=None):
    """Simulate payoff across a range of terminal spot prices."""
    if spots is None:
        spots = np.linspace(0.8 * params["S"], 1.2 * params["S"], 5)
    cf0, pnls = simulate_trade(params, trade, S_future=spots)
    return cf0, pnls

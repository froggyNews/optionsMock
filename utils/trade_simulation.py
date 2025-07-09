import numpy as np

TRADE_MAP = {
    "Buy call, sell put, buy stock, borrow PV(K)": {
        "call": 1,
        "put": -1,
        "stock": 1,
        "pvk": 1,
    },
    "Sell call, buy put, short stock, lend PV(K)": {
        "call": -1,
        "put": 1,
        "stock": -1,
        "pvk": -1,
    },
    "No arbitrage": {
        "call": 0,
        "put": 0,
        "stock": 0,
        "pvk": 0,
    },
}


def pv_k(K, r, T):
    """Present value of the strike."""
    return K * np.exp(-r * T)


def trade_from_choices(call_choice, put_choice, stock_choice, pvk_choice, call_qty, put_qty, stock_qty):
    """Convert user selections and quantities to trade sign dictionary."""
    choice_map = {
        "Buy": 1, "Sell": -1, "None": 0,
        "Long": 1, "Short": -1,
        "Borrow": 1, "Lend": -1
    }
    return {
        "call": choice_map.get(call_choice.split()[0], 0) * call_qty,
        "put": choice_map.get(put_choice.split()[0], 0) * put_qty,
        "stock": choice_map.get(stock_choice.split()[0], 0) * stock_qty,
        "pvk": choice_map.get(pvk_choice.split()[0], 0),
    }


def simulate_trade(params, trade, S_future=(90, 100, 110, 120, 130)):
    """Return initial cash flow and P&L for each future stock price."""
    C = params.get("C", params.get("C_mkt"))
    P = params.get("P", params.get("P_mkt"))
    S0 = params["S"]
    K = params["K"]
    r = params["r"]
    T = params["T"]
    pvk = pv_k(K, r, T)

    cf0 = (
        -trade["call"] * C
        - trade["put"] * P
        - trade["stock"] * S0
        + trade["pvk"] * pvk
    )

    results = {}
    for ST in S_future:
        call_payoff = max(ST - K, 0)
        put_payoff = max(K - ST, 0)
        end = (
            trade["call"] * call_payoff
            + trade["put"] * put_payoff
            + trade["stock"] * ST
            - trade["pvk"] * K
        )
        results[ST] = cf0 + end

    return cf0, results
import numpy as np
from scipy.stats import norm


def d1(S, K, r, T, sigma, q=0.0):
    """Calculate d1 for Black-Scholes formula."""
    S, K, T, sigma = map(np.asarray, (S, K, T, sigma))
    return (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T))


def d2(S, K, r, T, sigma, q=0.0):
    """Calculate d2 for Black-Scholes formula."""
    return d1(S, K, r, T, sigma, q) - sigma * np.sqrt(T)


def call_price(S, K, r, T, sigma, q=0.0):
    """Black-Scholes price of a European call option."""
    D1 = d1(S, K, r, T, sigma, q)
    D2 = D1 - sigma * np.sqrt(T)
    return S * np.exp(-q * T) * norm.cdf(D1) - K * np.exp(-r * T) * norm.cdf(D2)


def put_price(S, K, r, T, sigma, q=0.0):
    """Black-Scholes price of a European put option."""
    D1 = d1(S, K, r, T, sigma, q)
    D2 = D1 - sigma * np.sqrt(T)
    return K * np.exp(-r * T) * norm.cdf(-D2) - S * np.exp(-q * T) * norm.cdf(-D1)


# ---- Greeks ----

def call_delta(S, K, r, T, sigma, q=0.0):
    """Delta of a European call."""
    return np.exp(-q * T) * norm.cdf(d1(S, K, r, T, sigma, q))


def put_delta(S, K, r, T, sigma, q=0.0):
    """Delta of a European put."""
    return np.exp(-q * T) * (norm.cdf(d1(S, K, r, T, sigma, q)) - 1)


def gamma(S, K, r, T, sigma, q=0.0):
    """Gamma is the same for calls and puts."""
    D1 = d1(S, K, r, T, sigma, q)
    return np.exp(-q * T) * norm.pdf(D1) / (S * sigma * np.sqrt(T))


def vega(S, K, r, T, sigma, q=0.0):
    """Vega: sensitivity to volatility (per 1% change)."""
    D1 = d1(S, K, r, T, sigma, q)
    return S * np.exp(-q * T) * norm.pdf(D1) * np.sqrt(T) / 100


def call_theta(S, K, r, T, sigma, q=0.0):
    """Theta of a European call (per day)."""
    D1 = d1(S, K, r, T, sigma, q)
    D2 = D1 - sigma * np.sqrt(T)
    term1 = -S * norm.pdf(D1) * sigma * np.exp(-q * T) / (2 * np.sqrt(T))
    term2 = q * S * norm.cdf(D1) * np.exp(-q * T)
    term3 = r * K * np.exp(-r * T) * norm.cdf(D2)
    return (term1 - term2 - term3) / 365


def put_theta(S, K, r, T, sigma, q=0.0):
    """Theta of a European put (per day)."""
    D1 = d1(S, K, r, T, sigma, q)
    D2 = D1 - sigma * np.sqrt(T)
    term1 = -S * norm.pdf(D1) * sigma * np.exp(-q * T) / (2 * np.sqrt(T))
    term2 = q * S * norm.cdf(-D1) * np.exp(-q * T)
    term3 = r * K * np.exp(-r * T) * norm.cdf(-D2)
    return (term1 + term2 - term3) / 365


def call_rho(S, K, r, T, sigma, q=0.0):
    """Rho of a European call (per 1% rate change)."""
    D2 = d2(S, K, r, T, sigma, q)
    return K * T * np.exp(-r * T) * norm.cdf(D2) / 100


def put_rho(S, K, r, T, sigma, q=0.0):
    """Rho of a European put (per 1% rate change)."""
    D2 = d2(S, K, r, T, sigma, q)
    return -K * T * np.exp(-r * T) * norm.cdf(-D2) / 100

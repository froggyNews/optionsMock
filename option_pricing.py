import numpy as np
from scipy.stats import norm


def d1(S, K, r, T, sigma):
    return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))


def d2(S, K, r, T, sigma):
    return d1(S, K, r, T, sigma) - sigma * np.sqrt(T)


def call_price(S, K, r, T, sigma):
    """Black-Scholes call price"""
    D1 = d1(S, K, r, T, sigma)
    D2 = d2(S, K, r, T, sigma)
    return S * norm.cdf(D1) - K * np.exp(-r * T) * norm.cdf(D2)


def put_price(S, K, r, T, sigma):
    """Black-Scholes put price"""
    D1 = d1(S, K, r, T, sigma)
    D2 = d2(S, K, r, T, sigma)
    return K * np.exp(-r * T) * norm.cdf(-D2) - S * norm.cdf(-D1)


def call_delta(S, K, r, T, sigma):
    return norm.cdf(d1(S, K, r, T, sigma))


def put_delta(S, K, r, T, sigma):
    return call_delta(S, K, r, T, sigma) - 1


def gamma(S, K, r, T, sigma):
    """Black-Scholes gamma (same for calls and puts)"""
    D1 = d1(S, K, r, T, sigma)
    return norm.pdf(D1) / (S * sigma * np.sqrt(T))


def vega(S, K, r, T, sigma):
    """Black-Scholes vega (same for calls and puts)"""
    D1 = d1(S, K, r, T, sigma)
    return S * norm.pdf(D1) * np.sqrt(T)


def call_theta(S, K, r, T, sigma):
    """Black-Scholes theta for a call"""
    D1 = d1(S, K, r, T, sigma)
    D2 = d2(S, K, r, T, sigma)
    term1 = -(S * norm.pdf(D1) * sigma) / (2 * np.sqrt(T))
    term2 = r * K * np.exp(-r * T) * norm.cdf(D2)
    return term1 - term2


def put_theta(S, K, r, T, sigma):
    """Black-Scholes theta for a put"""
    D1 = d1(S, K, r, T, sigma)
    D2 = d2(S, K, r, T, sigma)
    term1 = -(S * norm.pdf(D1) * sigma) / (2 * np.sqrt(T))
    term2 = r * K * np.exp(-r * T) * norm.cdf(-D2)
    return term1 + term2


def call_rho(S, K, r, T, sigma):
    """Black-Scholes rho for a call"""
    D2 = d2(S, K, r, T, sigma)
    return K * T * np.exp(-r * T) * norm.cdf(D2)


def put_rho(S, K, r, T, sigma):
    """Black-Scholes rho for a put"""
    D2 = d2(S, K, r, T, sigma)
    return -K * T * np.exp(-r * T) * norm.cdf(-D2)

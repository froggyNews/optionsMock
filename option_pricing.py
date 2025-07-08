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

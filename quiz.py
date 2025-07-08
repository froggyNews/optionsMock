import random
import time
from pathlib import Path

import pandas as pd


QUESTIONS = [
    {
        "question": "Which Greek measures sensitivity of option price to underlying price?",
        "options": ["Delta", "Gamma", "Theta", "Vega"],
        "answer": 0,
        "topic": "Delta",
        "difficulty": "Easy",
        "explanation": "Delta is the first derivative of the option price with respect to the underlying price.",
    },
    {
        "question": "If put-call parity is violated with C - P > S - Ke^{-rT}, what trade exploits it?",
        "options": [
            "Buy call, sell put, buy stock, borrow PV(K)",
            "Sell call, buy put, short stock, lend PV(K)",
            "Buy call and put",
            "Do nothing",
        ],
        "answer": 1,
        "topic": "Parity",
        "difficulty": "Hard",
        "explanation": "When C - P is too high you should sell the call, buy the put, short the stock and lend the present value of K.",
    },
    {
        "question": "Which Greek measures sensitivity of option price to volatility?",
        "options": ["Theta", "Gamma", "Vega", "Rho"],
        "answer": 2,
        "topic": "Greeks",
        "difficulty": "Medium",
        "explanation": "Vega is the change in option price for a 1% change in volatility.",
    },
    {
        "question": "What does delta hedging attempt to neutralize?",
        "options": ["Gamma risk", "Time decay", "Price risk", "Interest rate risk"],
        "answer": 2,
        "topic": "Hedging",
        "difficulty": "Medium",
        "explanation": "By taking an offsetting position in the underlying, delta hedging neutralizes price risk of small moves.",
    },
    {
        "question": "A riskless profit opportunity with zero net investment is known as?",
        "options": ["Hedge", "Speculation", "Arbitrage", "Diversification"],
        "answer": 2,
        "topic": "Arbitrage",
        "difficulty": "Easy",
        "explanation": "Arbitrage is the practice of locking in a riskless profit with no initial cost.",
    },
]

HISTORY_FILE = Path("quiz_history.csv")
TIME_LIMIT = 30  # seconds per question


def time_left(start_time):
    """Return remaining seconds before time limit expires."""
    return max(0, TIME_LIMIT - int(time.time() - start_time))


def ask_question(idx=None, difficulty=None):
    pool = QUESTIONS
    if difficulty:
        pool = [q for q in QUESTIONS if q["difficulty"] == difficulty]
    if not pool:
        pool = QUESTIONS
    if idx is None:
        idx = random.randrange(len(pool))
    q = pool[idx]
    return q, idx


def record_result(correct, topic):
    df = pd.DataFrame([{"correct": int(correct), "topic": topic}])
    if HISTORY_FILE.exists():
        df_all = pd.read_csv(HISTORY_FILE)
        df_all = pd.concat([df_all, df], ignore_index=True)
    else:
        df_all = df
    df_all.to_csv(HISTORY_FILE, index=False)


def _streak(correct_series):
    streak = 0
    for val in reversed(correct_series):
        if val:
            streak += 1
        else:
            break
    return streak


def load_history():
    if HISTORY_FILE.exists():
        df = pd.read_csv(HISTORY_FILE)
        score = df["correct"].sum()
        total = len(df)
        accuracy = score / total if total else 0.0
        streak = _streak(df["correct"].tolist())
        # compute high score (max streak)
        max_streak = 0
        current = 0
        for val in df["correct"]:
            if val:
                current += 1
                max_streak = max(max_streak, current)
            else:
                current = 0
        by_topic = (
            df.groupby("topic")["correct"].agg(["sum", "count"]).to_dict(orient="index")
        )
        return score, total, accuracy, streak, max_streak, by_topic
    return 0, 0, 0.0, 0, 0, {}

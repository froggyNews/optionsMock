import random
import pandas as pd
from pathlib import Path


QUESTIONS = [
    {
        "question": "Which Greek measures sensitivity of option price to underlying price?",
        "options": ["Delta", "Gamma", "Theta", "Vega"],
        "answer": 0,
    },
    {
        "question": "If put-call parity is violated with C - P > S - Ke^{-rT}, what trade exploits it?",
        "options": [
            "Buy call, sell put, buy stock, borrow PV(K)",
            "Sell call, buy put, short stock, lend PV(K)",
            "Buy call and put", "Do nothing",
        ],
        "answer": 1,
    },
    {
        "question": "Delta of a call option is typically between?",
        "options": ["0 and 1", "-1 and 0", "1 and 2", "-2 and -1"],
        "answer": 0,
    },
]

HISTORY_FILE = Path("quiz_history.csv")


def ask_question(idx=None):
    if idx is None:
        idx = random.randrange(len(QUESTIONS))
    q = QUESTIONS[idx]
    return q["question"], q["options"], q["answer"], idx


def record_result(correct):
    df = pd.DataFrame([{"correct": int(correct)}])
    if HISTORY_FILE.exists():
        df_all = pd.read_csv(HISTORY_FILE)
        df_all = pd.concat([df_all, df], ignore_index=True)
    else:
        df_all = df
    df_all.to_csv(HISTORY_FILE, index=False)


def load_history():
    if HISTORY_FILE.exists():
        df = pd.read_csv(HISTORY_FILE)
        score = df["correct"].sum()
        total = len(df)
        return score, total
    return 0, 0

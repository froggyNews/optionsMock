# optionsMock

An interactive Streamlit app for practicing options trading concepts. The app includes:

- **Put-Call Parity Practice** with randomly generated parameters
- **Delta Hedging Simulation** using a simple random walk
- **Quiz Mode** to test knowledge of options theory

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   streamlit run app.py
   ```

## Requirements

- Python 3.8+
- Streamlit, NumPy, SciPy, Matplotlib, pandas

## Project Structure

- `app.py` – Streamlit application entry point
- `option_pricing.py` – Black-Scholes utilities and Greek calculations
- `parity.py` – Functions for put-call parity practice
- `delta_hedging.py` – Helpers for delta hedging simulation
- `quiz.py` – Quiz logic
Quiz results are stored in `quiz_history.csv`.

This project is intended for use on Windows systems.

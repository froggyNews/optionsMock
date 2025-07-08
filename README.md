# optionsMock

An interactive Streamlit app for practicing options trading concepts. The app includes:

- **Put-Call Parity Practice** with randomly generated parameters
- **Delta Hedging Simulation** using a simple random walk
- **Interactive Arbitrage Trainer** with scenario generation and Greek feedback
- **Quiz Mode** to test knowledge of options theory

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   streamlit run streamlit_app.py
   ```

## Requirements

- Python 3.8+
- Streamlit, NumPy, SciPy, Matplotlib, pandas

## Project Structure

- `streamlit_app.py` – Main Streamlit application with links to pages
- `pages/` – Individual app pages (parity, hedging, quiz, trading)
- `utils/option_pricing.py` – Black-Scholes utilities and Greek calculations
- `utils/scenario_generator.py` – Random scenario helper
- `utils/greeks.py` – Net Greeks computation
- `quiz_history.csv` stores quiz results

This project is intended for use on Windows systems.

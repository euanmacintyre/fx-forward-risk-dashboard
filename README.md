# FX and Rates Pricing Demo

A small Python toolkit plus Streamlit dashboard for pricing an FX forward, running simple risk scenarios, and generating a one page client note.

This is a learning project focused on clean pricing logic, clear assumptions, and a demo you can run locally.

## What it does
- Prices an FX forward using discount curves for base and quote currencies
- Shows PV in the quote currency
- Runs spot and curve shock scenarios and reports PnL vs base
- Exports a client note in Markdown

## Conventions
- Pair is BASE/QUOTE, for example EUR/USD
- Spot is QUOTE per 1 BASE
- Domestic currency is QUOTE, foreign currency is BASE
- PV is reported in the quote currency

## Live spot
The app fetches an indicative spot rate.
It uses Twelve Data if `TWELVEDATA_API_KEY` is set.
If not, it falls back to Frankfurter which is typically end of day.

To enable Twelve Data:
- copy `.env.example` to `.env`
- set `TWELVEDATA_API_KEY`

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e ".[dev]"
pytest -q
streamlit run apps/streamlit_app.py
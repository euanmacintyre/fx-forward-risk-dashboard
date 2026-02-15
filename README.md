# FX & Rates Pricing Demo

A compact Python project for FX forward and vanilla rates demo analytics.
It includes a reusable package (`fm_toolkit`), a Streamlit app, a CLI, scenario analysis, and markdown client note export.

## What It Does

- Prices FX forwards using domestic and foreign discount curves.
- Computes fair forward and present value (PV) in domestic currency.
- Runs spot and curve-shock scenarios with PnL vs base.
- Provides simple swap pricing and PV01 examples.
- Generates a one-page markdown client note.

## Conventions

- Currency pair format is `BASE/QUOTE` (for example, `EUR/USD`).
- Spot is quoted as `QUOTE` per 1 unit of `BASE`.
- FX forward PV is shown in domestic (`QUOTE`) currency.
- Curves are user-supplied zero curves with continuous compounding.

## Run Locally

Install the package first (editable mode) before running the app:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e ".[dev]"
ruff format --check .
ruff check .
pytest -q
streamlit run apps/streamlit_app.py
```

## Live Spot Notes

- The app fetches indicative live FX spot for common pairs.
- If `TWELVEDATA_API_KEY` is set, it attempts Twelve Data first.
- If Twelve Data is unavailable or the key is missing, it falls back to Frankfurter.
- Spot fetch is cached in Streamlit for 60 seconds.

Use `.env.example` as a template for local configuration.

## Disclaimer

- Spot values are indicative and may be delayed depending on provider.
- Pricing and risk outputs are for demonstration only and not trading or risk advice.
- Curve inputs are user-provided and materially affect results.

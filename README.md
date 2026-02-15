# FX & Rates Pricing Demo

A compact Python project for FX forward and vanilla rates demo analytics. It includes a reusable package (`fm_toolkit`), a Streamlit app, a CLI, scenario analysis, and markdown client-note export.

## What It Is

This repo is a practical demo of:

- Curve-based FX forward pricing.
- Basic rates analytics (swap PV / PV01).
- Scenario analysis and markdown reporting.
- Live indicative spot integration with fallback providers.

## Features

- FX forward fair value and PV using domestic/foreign zero curves.
- Spot and curve shock scenarios with PnL vs base.
- Streamlit dashboard for interactive what-if analysis.
- CLI demo entrypoint for quick local checks.
- One-page markdown client note download.

## Quickstart

Install dependencies before running Streamlit:

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

## Screenshot Placeholder

![Streamlit app screenshot placeholder](docs/screenshot.png)

To add a real screenshot:

1. Run the app locally.
2. Capture the main dashboard.
3. Save the image as `docs/screenshot.png` (replace the placeholder file).

## Live Spot Providers

- The app fetches indicative spot for common pairs.
- Provider order:
  - Twelve Data (`TWELVEDATA_API_KEY`)
  - Frankfurter fallback (no key)
- Spot fetches are cached in Streamlit for 60 seconds.

Set up environment variables using `.env.example`:

```bash
cp .env.example .env
# then set TWELVEDATA_API_KEY in .env
```

If `TWELVEDATA_API_KEY` is missing or Twelve Data fails, the app automatically falls back to Frankfurter.

## Disclaimer

- Spot values are indicative and may be delayed depending on provider.
- Pricing and risk outputs are for demonstration only and not trading/risk advice.
- Curves are user-supplied inputs and materially affect results.

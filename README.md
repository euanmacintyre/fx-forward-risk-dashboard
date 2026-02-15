# ING FM Python Package Demo

This repository is a compact `src`-layout Python project for basic Financial Markets pricing and risk examples.

## Structure

```text
.
|-- pyproject.toml
|-- src/ing_fm/
|   |-- curves.py
|   |-- fx_forwards.py
|   |-- swaps.py
|   |-- risk.py
|   |-- scenarios.py
|   `-- report.py
|-- apps/
|   |-- cli.py
|   `-- streamlit_app.py
`-- tests/
```

## Exact Run Commands

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
pytest
python apps/cli.py demo
python apps/cli.py fx-forward --notional 5000000 --spot 1.10 --strike 1.12 --domestic-rate 0.03 --foreign-rate 0.015 --maturity 1.0
python apps/cli.py swap --notional 10000000 --fixed-rate 0.03 --maturity 5 --payments-per-year 2 --pay-fixed
streamlit run apps/streamlit_app.py
```

## Notes

- FX forward pricing supports full domestic/foreign discount curves:
  - `F = S * DF_foreign(T) / DF_domestic(T)`
  - Flat-rate calls are still supported for backward compatibility.
- In the Streamlit FX tab, edit domestic/foreign tenor-rate tables (`1M`, `3M`, `6M`, `1Y`, `2Y`) to see fair forward update from curve shape changes.
- The Streamlit FX tab includes a scenario table with configurable `spot_shock_pct` and `rate_shock_bps`.
- The Streamlit FX tab includes a `Download Client Note (Markdown)` button that exports `ing_fm_client_note.md`.
- `tests/test_fx_forwards.py` covers FX forward no-arbitrage behavior plus curve-based tenor sensitivity.
- `tests/test_swaps.py` covers swap par pricing and PV01 directionality.

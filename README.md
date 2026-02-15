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

- `tests/test_fx_forwards.py` covers FX forward no-arbitrage behavior.
- `tests/test_swaps.py` covers swap par pricing and PV01 directionality.

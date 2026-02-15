"""Streamlit demo app for FX & rates pricing."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from fm_toolkit.curves import ZeroCurve
from fm_toolkit.fx_forwards import forward_rate, price_fx_forward
from fm_toolkit.marketdata import get_live_spot, parse_pair
from fm_toolkit.report import build_fx_forward_client_note
from fm_toolkit.scenarios import fx_forward_scenarios
from fm_toolkit.swaps import VanillaSwap, par_swap_rate, swap_pv, swap_pv01

_COMMON_PAIRS = ["EUR/USD", "GBP/USD", "USD/JPY", "EUR/GBP", "AUD/USD"]


def _build_curve_from_table(table: pd.DataFrame, curve_name: str) -> ZeroCurve:
    tenors: list[str] = []
    zero_rates: list[float] = []

    for _, row in table.iterrows():
        tenor_raw = str(row.get("tenor", "")).strip()
        rate_raw = row.get("zero_rate", None)
        if tenor_raw == "":
            continue
        if rate_raw in ("", None):
            raise ValueError(f"{curve_name}: zero_rate is missing for tenor {tenor_raw}")

        tenors.append(tenor_raw)
        zero_rates.append(float(rate_raw))

    if not tenors:
        raise ValueError(f"{curve_name}: at least one tenor/rate row is required")
    return ZeroCurve.from_tenors(tenors=tenors, zero_rates=zero_rates)


@st.cache_data(ttl=60)
def _fetch_cached_spot(pair: str) -> tuple[float, str, str]:
    base, quote = parse_pair(pair)
    return get_live_spot(base=base, quote=quote)


st.set_page_config(page_title="FX & Rates Pricing Demo", layout="wide")
st.title("FX & Rates Pricing Demo")

fx_tab, swap_tab = st.tabs(["FX Forward", "Swap"])

with fx_tab:
    st.subheader("FX Forward")
    c1, c2, c3, c4 = st.columns(4)
    pair = c1.selectbox("Pair", options=_COMMON_PAIRS, index=0, key="fx_pair_select")
    manual_override = c2.checkbox("Manual override", value=False, key="fx_manual_spot_override")
    strike = c3.number_input("Strike", value=1.12, format="%.6f")
    notional = c4.number_input("Base Notional", value=5_000_000.0, step=100_000.0)

    live_source = "Unavailable"
    live_ts = "Unavailable"
    fallback_spot = float(st.session_state.get("fx_spot_value", 1.10))
    try:
        fetched_spot, live_ts, live_source = _fetch_cached_spot(pair)
    except RuntimeError as exc:
        st.warning(f"Live spot fetch failed for {pair}: {exc}")
        fetched_spot = fallback_spot

    if "fx_spot_value" not in st.session_state:
        st.session_state["fx_spot_value"] = float(fetched_spot)
    if not manual_override:
        st.session_state["fx_spot_value"] = float(fetched_spot)

    spot = st.number_input("Spot", key="fx_spot_value", format="%.6f")
    st.caption(f"Source: {live_source} | Last updated: {live_ts}")

    maturity = st.number_input("Maturity (years)", value=1.0, step=0.25, min_value=0.01)

    default_tenors = ["1M", "3M", "6M", "1Y", "2Y"]
    domestic_defaults = pd.DataFrame(
        {
            "tenor": default_tenors,
            "zero_rate": [0.024, 0.025, 0.026, 0.027, 0.028],
        }
    )
    foreign_defaults = pd.DataFrame(
        {
            "tenor": default_tenors,
            "zero_rate": [0.015, 0.016, 0.017, 0.018, 0.019],
        }
    )

    t1, t2 = st.columns(2)
    with t1:
        st.markdown("**Domestic Curve (tenor / zero_rate)**")
        domestic_table = st.data_editor(
            domestic_defaults,
            key="domestic_curve_editor",
            num_rows="dynamic",
            use_container_width=True,
        )
    with t2:
        st.markdown("**Foreign Curve (tenor / zero_rate)**")
        foreign_table = st.data_editor(
            foreign_defaults,
            key="foreign_curve_editor",
            num_rows="dynamic",
            use_container_width=True,
        )

    try:
        domestic_curve = _build_curve_from_table(domestic_table, "Domestic curve")
        foreign_curve = _build_curve_from_table(foreign_table, "Foreign curve")
    except ValueError as exc:
        st.error(str(exc))
    else:
        fair = forward_rate(
            spot=spot,
            maturity_years=maturity,
            domestic_curve=domestic_curve,
            foreign_curve=foreign_curve,
        )
        pv = price_fx_forward(
            notional_base=notional,
            strike=strike,
            spot=spot,
            maturity_years=maturity,
            domestic_curve=domestic_curve,
            foreign_curve=foreign_curve,
        )

        st.metric("Fair Forward", f"{fair:.6f}")
        st.metric("PV (domestic)", f"{pv:,.2f}")
        st.caption(
            f"Interpolated zero rates at T={maturity:.2f}Y | "
            f"Domestic: {domestic_curve.zero_rate(maturity):.4%}, "
            f"Foreign: {foreign_curve.zero_rate(maturity):.4%}"
        )

        st.markdown("### FX Forward Scenarios")
        sc1, sc2 = st.columns(2)
        scenario_spot_shock_pct = sc1.number_input(
            "spot_shock_pct",
            value=1.0,
            step=0.1,
            help="Scenario spot shock size in percent (1.0 means 1%).",
        )
        scenario_rate_shock_bps = sc2.number_input(
            "rate_shock_bps",
            value=25.0,
            step=1.0,
            help="Parallel curve shock in basis points.",
        )

        scenario_df = fx_forward_scenarios(
            notional_base=notional,
            strike=strike,
            spot=spot,
            maturity_years=maturity,
            domestic_curve=domestic_curve,
            foreign_curve=foreign_curve,
            spot_shock_pct=scenario_spot_shock_pct,
            rate_shock_bps=scenario_rate_shock_bps,
        )
        st.dataframe(scenario_df, use_container_width=True)

        client_note_md = build_fx_forward_client_note(
            pair=pair,
            notional_base=notional,
            maturity_years=maturity,
            strike=strike,
            spot=spot,
            domestic_curve=domestic_curve,
            foreign_curve=foreign_curve,
            fair_forward=fair,
            pv=pv,
            scenario_df=scenario_df,
            spot_shock_pct=scenario_spot_shock_pct,
            rate_shock_bps=scenario_rate_shock_bps,
        )
        st.download_button(
            label="Download Client Note (Markdown)",
            data=client_note_md,
            file_name="fm_toolkit_client_note.md",
            mime="text/markdown",
        )

with swap_tab:
    st.subheader("Vanilla Swap")
    curve = ZeroCurve(times=[1, 2, 3, 5, 10], zero_rates=[0.02, 0.022, 0.024, 0.026, 0.028])

    s1, s2, s3, s4 = st.columns(4)
    maturity_years = s1.number_input("Maturity", value=5.0, step=1.0)
    fixed_rate = s2.number_input("Fixed Rate", value=0.03, format="%.4f")
    payments_per_year = int(s3.selectbox("Payments / Year", options=[1, 2, 4], index=1))
    notional_swap = s4.number_input("Notional", value=10_000_000.0, step=100_000.0)
    pay_fixed = st.checkbox("Pay Fixed", value=True)

    par = par_swap_rate(curve, maturity_years, payments_per_year)
    swap = VanillaSwap(
        notional=notional_swap,
        fixed_rate=fixed_rate,
        maturity_years=maturity_years,
        payments_per_year=payments_per_year,
        pay_fixed=pay_fixed,
    )

    pv = swap_pv(swap, curve)
    pv01 = swap_pv01(swap, curve)

    st.metric("Par Rate", f"{par:.4%}")
    st.metric("Swap PV", f"{pv:,.2f}")
    st.metric("Swap PV01 (+1bp)", f"{pv01:,.2f}")

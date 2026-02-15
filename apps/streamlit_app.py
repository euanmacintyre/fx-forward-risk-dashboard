"""Streamlit demo app for ING FM pricing."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from ing_fm.curves import ZeroCurve
from ing_fm.fx_forwards import forward_rate, price_fx_forward
from ing_fm.swaps import VanillaSwap, par_swap_rate, swap_pv, swap_pv01


st.set_page_config(page_title="ING FM Demo", layout="wide")
st.title("ING FM Pricing Demo")

fx_tab, swap_tab = st.tabs(["FX Forward", "Swap"])

with fx_tab:
    st.subheader("FX Forward")
    c1, c2, c3 = st.columns(3)
    spot = c1.number_input("Spot", value=1.10, format="%.6f")
    strike = c2.number_input("Strike", value=1.12, format="%.6f")
    notional = c3.number_input("Base Notional", value=5_000_000.0, step=100_000.0)

    d1, d2, d3 = st.columns(3)
    domestic_rate = d1.number_input("Domestic Rate", value=0.03, format="%.4f")
    foreign_rate = d2.number_input("Foreign Rate", value=0.015, format="%.4f")
    maturity = d3.number_input("Maturity (years)", value=1.0, step=0.25)

    fair = forward_rate(spot, domestic_rate, foreign_rate, maturity)
    pv = price_fx_forward(notional, strike, spot, domestic_rate, foreign_rate, maturity)

    st.metric("Fair Forward", f"{fair:.6f}")
    st.metric("PV (domestic)", f"{pv:,.2f}")

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

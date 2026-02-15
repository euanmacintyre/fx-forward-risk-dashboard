"""Simple text report for demo pricing outputs."""

from __future__ import annotations

from .curves import ZeroCurve
from .fx_forwards import forward_rate, price_fx_forward
from .swaps import VanillaSwap, par_swap_rate, swap_pv, swap_pv01


def build_demo_report() -> str:
    curve = ZeroCurve(times=[1, 2, 3, 5, 10], zero_rates=[0.02, 0.022, 0.024, 0.026, 0.028])

    spot = 1.10
    rd = 0.03
    rf = 0.015
    tenor = 1.0
    strike = 1.12
    fx_notional = 5_000_000

    fair_fwd = forward_rate(spot=spot, domestic_rate=rd, foreign_rate=rf, maturity_years=tenor)
    fx_pv = price_fx_forward(
        notional_base=fx_notional,
        strike=strike,
        spot=spot,
        domestic_rate=rd,
        foreign_rate=rf,
        maturity_years=tenor,
    )

    maturity = 5
    pay_freq = 2
    par_rate = par_swap_rate(curve=curve, maturity_years=maturity, payments_per_year=pay_freq)
    swap = VanillaSwap(
        notional=10_000_000,
        fixed_rate=par_rate + 0.0025,
        maturity_years=maturity,
        payments_per_year=pay_freq,
        pay_fixed=True,
    )
    swap_value = swap_pv(swap=swap, curve=curve)
    pv01 = swap_pv01(swap=swap, curve=curve)

    lines = [
        "ING FM Demo Report",
        "==================",
        f"FX fair forward: {fair_fwd:.6f}",
        f"FX forward PV (domestic): {fx_pv:,.2f}",
        f"Swap par rate: {par_rate:.4%}",
        f"Swap PV: {swap_value:,.2f}",
        f"Swap PV01 (+1bp): {pv01:,.2f}",
    ]
    return "\n".join(lines)

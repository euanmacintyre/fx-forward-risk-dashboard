"""Simple text report for demo pricing outputs."""

from __future__ import annotations

import pandas as pd

from .curves import ZeroCurve
from .fx_forwards import forward_rate, price_fx_forward
from .scenarios import fx_forward_scenarios
from .swaps import VanillaSwap, par_swap_rate, swap_pv, swap_pv01


def _markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    header_line = "| " + " | ".join(headers) + " |"
    divider_line = "| " + " | ".join(["---"] * len(headers)) + " |"
    body_lines = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header_line, divider_line, *body_lines])


def _curve_points_table(curve: ZeroCurve, max_points: int = 5) -> str:
    rows: list[list[str]] = []
    for t, r in list(zip(curve.times, curve.zero_rates))[:max_points]:
        rows.append([f"{t:.4f}", f"{r:.4%}"])
    return _markdown_table(["Pillar (Y)", "Zero Rate"], rows)


def _pv_explanation(strike: float, fair_forward: float, pv: float) -> str:
    if abs(pv) < 1e-8:
        return (
            "The chosen strike is effectively at the market fair forward, so the trade is near zero value today."
        )
    if pv > 0:
        return (
            "PV is positive because the agreed strike is below the current fair forward, "
            "which is favorable for this long-base forward position."
        )
    return (
        "PV is negative because the agreed strike is above the current fair forward, "
        "so the locked level is currently less favorable for this long-base forward position."
    )


def _scenario_markdown_table(scenario_df: pd.DataFrame, top_n: int = 6) -> str:
    subset = scenario_df.head(top_n).copy()
    rows: list[list[str]] = []
    for _, row in subset.iterrows():
        rows.append(
            [
                str(row["Scenario name"]),
                f"{float(row['Spot shock (pct)']):.2f}",
                f"{float(row['Domestic curve shock (bps)']):.2f}",
                f"{float(row['Foreign curve shock (bps)']):.2f}",
                f"{float(row['PV (domestic)']):,.2f}",
                f"{float(row['PnL vs base']):,.2f}",
            ]
        )
    return _markdown_table(
        [
            "Scenario name",
            "Spot shock (pct)",
            "Domestic curve shock (bps)",
            "Foreign curve shock (bps)",
            "PV (domestic)",
            "PnL vs base",
        ],
        rows,
    )


def build_fx_forward_client_note(
    *,
    pair: str,
    notional_base: float,
    maturity_years: float,
    strike: float,
    spot: float,
    domestic_curve: ZeroCurve,
    foreign_curve: ZeroCurve,
    fair_forward: float | None = None,
    pv: float | None = None,
    scenario_df: pd.DataFrame | None = None,
    spot_shock_pct: float = 1.0,
    rate_shock_bps: float = 25.0,
) -> str:
    """Build a one-page markdown client note for an FX forward."""

    if fair_forward is None:
        fair_forward = forward_rate(
            spot=spot,
            maturity_years=maturity_years,
            domestic_curve=domestic_curve,
            foreign_curve=foreign_curve,
        )
    if pv is None:
        pv = price_fx_forward(
            notional_base=notional_base,
            strike=strike,
            spot=spot,
            maturity_years=maturity_years,
            domestic_curve=domestic_curve,
            foreign_curve=foreign_curve,
        )
    if scenario_df is None:
        scenario_df = fx_forward_scenarios(
            notional_base=notional_base,
            strike=strike,
            spot=spot,
            maturity_years=maturity_years,
            domestic_curve=domestic_curve,
            foreign_curve=foreign_curve,
            spot_shock_pct=spot_shock_pct,
            rate_shock_bps=rate_shock_bps,
        )

    explanation = _pv_explanation(strike=strike, fair_forward=fair_forward, pv=pv)
    scenario_md = _scenario_markdown_table(scenario_df=scenario_df, top_n=6)

    lines = [
        "# FX & Rates Client Note - FX Forward",
        "",
        "## Trade Summary",
        f"- Pair: {pair}",
        f"- Base notional: {notional_base:,.0f}",
        f"- Maturity: {maturity_years:.2f} years",
        f"- Strike: {strike:.6f}",
        "",
        "## Market Snapshot",
        f"- Spot: {spot:.6f}",
        f"- Domestic zero rate at maturity: {domestic_curve.zero_rate(maturity_years):.4%}",
        f"- Foreign zero rate at maturity: {foreign_curve.zero_rate(maturity_years):.4%}",
        "",
        "### Domestic Curve Key Points",
        _curve_points_table(domestic_curve),
        "",
        "### Foreign Curve Key Points",
        _curve_points_table(foreign_curve),
        "",
        "## Pricing Summary",
        f"- Fair forward: {fair_forward:.6f}",
        f"- PV (domestic): {pv:,.2f}",
        f"- Interpretation: {explanation}",
        "",
        "## Scenario Summary (Top 6)",
        scenario_md,
        "",
        "## Next Steps",
        "- Share the quoted strike versus fair value and propose hedge timing based on the scenario PnL profile.",
    ]
    return "\n".join(lines)


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
        "FX & Rates Pricing Demo Report",
        "==================",
        f"FX fair forward: {fair_fwd:.6f}",
        f"FX forward PV (domestic): {fx_pv:,.2f}",
        f"Swap par rate: {par_rate:.4%}",
        f"Swap PV: {swap_value:,.2f}",
        f"Swap PV01 (+1bp): {pv01:,.2f}",
    ]
    return "\n".join(lines)

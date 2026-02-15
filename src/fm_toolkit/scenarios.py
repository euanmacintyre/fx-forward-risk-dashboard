"""Market scenario helpers."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .curves import ZeroCurve
from .fx_forwards import price_fx_forward


@dataclass
class MarketScenario:
    name: str
    parallel_rate_bump_bp: float = 0.0
    fx_spot_shock_pct: float = 0.0


def apply_curve_scenario(curve: ZeroCurve, scenario: MarketScenario) -> ZeroCurve:
    return curve.shifted(scenario.parallel_rate_bump_bp)


def apply_fx_scenario(spot: float, scenario: MarketScenario) -> float:
    return spot * (1.0 + scenario.fx_spot_shock_pct)


def fx_forward_scenarios(
    *,
    notional_base: float,
    strike: float,
    spot: float,
    maturity_years: float,
    domestic_curve: ZeroCurve,
    foreign_curve: ZeroCurve,
    spot_shock_pct: float = 1.0,
    rate_shock_bps: float = 25.0,
) -> pd.DataFrame:
    """Build a scenario table for FX forward PV/PnL.

    Parameters
    ----------
    spot_shock_pct:
        Shock size in percent, where 1.0 means 1%.
    rate_shock_bps:
        Parallel curve bump in basis points.
    """

    base_pv = price_fx_forward(
        notional_base=notional_base,
        strike=strike,
        spot=spot,
        maturity_years=maturity_years,
        domestic_curve=domestic_curve,
        foreign_curve=foreign_curve,
    )

    scenario_defs = [
        (f"Spot -{spot_shock_pct:g}%", -spot_shock_pct, 0.0, 0.0),
        (f"Spot +{spot_shock_pct:g}%", spot_shock_pct, 0.0, 0.0),
        (f"Domestic +{rate_shock_bps:g}bp", 0.0, rate_shock_bps, 0.0),
        (f"Domestic -{rate_shock_bps:g}bp", 0.0, -rate_shock_bps, 0.0),
        (f"Foreign +{rate_shock_bps:g}bp", 0.0, 0.0, rate_shock_bps),
        (f"Foreign -{rate_shock_bps:g}bp", 0.0, 0.0, -rate_shock_bps),
        (
            f"Spot +{spot_shock_pct:g}% & Domestic +{rate_shock_bps:g}bp",
            spot_shock_pct,
            rate_shock_bps,
            0.0,
        ),
        (
            f"Spot -{spot_shock_pct:g}% & Domestic -{rate_shock_bps:g}bp",
            -spot_shock_pct,
            -rate_shock_bps,
            0.0,
        ),
    ]

    rows: list[dict[str, float | str]] = []
    for name, spot_shock_pct_value, domestic_bps, foreign_bps in scenario_defs:
        shocked_spot = spot * (1.0 + spot_shock_pct_value / 100.0)
        shocked_domestic_curve = domestic_curve.shifted(domestic_bps)
        shocked_foreign_curve = foreign_curve.shifted(foreign_bps)

        pv = price_fx_forward(
            notional_base=notional_base,
            strike=strike,
            spot=shocked_spot,
            maturity_years=maturity_years,
            domestic_curve=shocked_domestic_curve,
            foreign_curve=shocked_foreign_curve,
        )
        rows.append(
            {
                "Scenario name": name,
                "Spot shock (pct)": spot_shock_pct_value,
                "Domestic curve shock (bps)": domestic_bps,
                "Foreign curve shock (bps)": foreign_bps,
                "PV (domestic)": pv,
                "PnL vs base": pv - base_pv,
            }
        )

    return pd.DataFrame(rows)

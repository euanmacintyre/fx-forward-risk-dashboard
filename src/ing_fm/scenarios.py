"""Market scenario helpers."""

from __future__ import annotations

from dataclasses import dataclass

from .curves import ZeroCurve


@dataclass
class MarketScenario:
    name: str
    parallel_rate_bump_bp: float = 0.0
    fx_spot_shock_pct: float = 0.0


def apply_curve_scenario(curve: ZeroCurve, scenario: MarketScenario) -> ZeroCurve:
    return curve.shifted(scenario.parallel_rate_bump_bp)


def apply_fx_scenario(spot: float, scenario: MarketScenario) -> float:
    return spot * (1.0 + scenario.fx_spot_shock_pct)

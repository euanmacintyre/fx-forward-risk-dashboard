"""Risk measures built on pricing modules."""

from __future__ import annotations

from .curves import ZeroCurve
from .fx_forwards import price_fx_forward
from .swaps import VanillaSwap, swap_pv01


def fx_forward_spot_delta(
    notional_base: float,
    strike: float,
    spot: float,
    domestic_rate: float,
    foreign_rate: float,
    maturity_years: float,
    rel_bump: float = 1e-4,
) -> float:
    """Finite-difference spot delta (PV change per +1.0 spot unit)."""

    base_pv = price_fx_forward(
        notional_base,
        strike,
        spot,
        domestic_rate,
        foreign_rate,
        maturity_years,
    )
    bumped_pv = price_fx_forward(
        notional_base,
        strike,
        spot * (1.0 + rel_bump),
        domestic_rate,
        foreign_rate,
        maturity_years,
    )
    return (bumped_pv - base_pv) / (spot * rel_bump)


def swap_parallel_dv01(swap: VanillaSwap, curve: ZeroCurve) -> float:
    """Dollar value change for a +1bp parallel shift."""

    return swap_pv01(swap=swap, curve=curve, bump_bp=1.0)

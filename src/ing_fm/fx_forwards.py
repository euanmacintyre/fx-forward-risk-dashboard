"""FX forward pricing helpers."""

from __future__ import annotations

from math import exp


def forward_rate(
    spot: float,
    domestic_rate: float,
    foreign_rate: float,
    maturity_years: float,
) -> float:
    """Covered-interest-parity FX forward under continuous compounding."""

    if maturity_years <= 0:
        raise ValueError("maturity_years must be positive")
    if spot <= 0:
        raise ValueError("spot must be positive")

    carry = (domestic_rate - foreign_rate) * maturity_years
    return spot * exp(carry)


def price_fx_forward(
    notional_base: float,
    strike: float,
    spot: float,
    domestic_rate: float,
    foreign_rate: float,
    maturity_years: float,
) -> float:
    """Present value in domestic currency for a long-base FX forward.

    Positive PV means the agreed strike is favorable versus the fair forward.
    """

    if notional_base <= 0:
        raise ValueError("notional_base must be positive")
    if strike <= 0:
        raise ValueError("strike must be positive")

    fair_fwd = forward_rate(
        spot=spot,
        domestic_rate=domestic_rate,
        foreign_rate=foreign_rate,
        maturity_years=maturity_years,
    )
    discount = exp(-domestic_rate * maturity_years)
    return notional_base * (fair_fwd - strike) * discount

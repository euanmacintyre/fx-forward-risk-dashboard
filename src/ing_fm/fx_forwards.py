"""FX forward pricing helpers."""

from __future__ import annotations

from .curves import ZeroCurve


def _flat_curve_from_rate(rate: float | None, rate_name: str, curve_name: str) -> ZeroCurve:
    if rate is None:
        raise ValueError(f"{rate_name} is required when {curve_name} is not provided")
    return ZeroCurve(times=[1.0], zero_rates=[float(rate)])


def _resolve_curves(
    domestic_curve: ZeroCurve | None,
    foreign_curve: ZeroCurve | None,
    domestic_rate: float | None,
    foreign_rate: float | None,
) -> tuple[ZeroCurve, ZeroCurve]:
    if domestic_curve is None:
        domestic_curve = _flat_curve_from_rate(domestic_rate, "domestic_rate", "domestic_curve")
    if foreign_curve is None:
        foreign_curve = _flat_curve_from_rate(foreign_rate, "foreign_rate", "foreign_curve")
    return domestic_curve, foreign_curve


def forward_rate(
    spot: float,
    domestic_rate: float | None = None,
    foreign_rate: float | None = None,
    maturity_years: float | None = None,
    *,
    domestic_curve: ZeroCurve | None = None,
    foreign_curve: ZeroCurve | None = None,
) -> float:
    """FX forward under discount-curve parity.

    Backward compatibility:
    - Old usage with flat rates still works (domestic_rate/foreign_rate).
    - New usage passes domestic_curve and foreign_curve.
    """

    if maturity_years is None or maturity_years <= 0:
        raise ValueError("maturity_years must be positive")
    if spot <= 0:
        raise ValueError("spot must be positive")

    domestic_curve, foreign_curve = _resolve_curves(
        domestic_curve=domestic_curve,
        foreign_curve=foreign_curve,
        domestic_rate=domestic_rate,
        foreign_rate=foreign_rate,
    )
    return spot * foreign_curve.df(maturity_years) / domestic_curve.df(maturity_years)


def price_fx_forward(
    notional_base: float,
    strike: float,
    spot: float,
    domestic_rate: float | None = None,
    foreign_rate: float | None = None,
    maturity_years: float | None = None,
    *,
    domestic_curve: ZeroCurve | None = None,
    foreign_curve: ZeroCurve | None = None,
) -> float:
    """Present value in domestic currency for a long-base FX forward.

    Positive PV means the agreed strike is favorable versus the fair forward.
    """

    if notional_base <= 0:
        raise ValueError("notional_base must be positive")
    if strike <= 0:
        raise ValueError("strike must be positive")
    if maturity_years is None or maturity_years <= 0:
        raise ValueError("maturity_years must be positive")

    domestic_curve, foreign_curve = _resolve_curves(
        domestic_curve=domestic_curve,
        foreign_curve=foreign_curve,
        domestic_rate=domestic_rate,
        foreign_rate=foreign_rate,
    )

    fair_fwd = forward_rate(
        spot=spot,
        domestic_curve=domestic_curve,
        foreign_curve=foreign_curve,
        maturity_years=maturity_years,
    )
    discount = domestic_curve.df(maturity_years)
    return notional_base * (fair_fwd - strike) * discount

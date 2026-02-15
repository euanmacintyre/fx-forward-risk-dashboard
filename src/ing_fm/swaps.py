"""Vanilla fixed-float IRS pricing and PV01."""

from __future__ import annotations

from dataclasses import dataclass

from .curves import ZeroCurve


@dataclass
class VanillaSwap:
    """Simple fixed-vs-floating interest rate swap."""

    notional: float
    fixed_rate: float
    maturity_years: float
    payments_per_year: int = 1
    pay_fixed: bool = True

    def __post_init__(self) -> None:
        if self.notional <= 0:
            raise ValueError("notional must be positive")
        if self.fixed_rate < 0:
            raise ValueError("fixed_rate must be non-negative")
        if self.maturity_years <= 0:
            raise ValueError("maturity_years must be positive")
        if self.payments_per_year <= 0:
            raise ValueError("payments_per_year must be positive")


def payment_times(maturity_years: float, payments_per_year: int) -> list[float]:
    periods = round(maturity_years * payments_per_year)
    if abs(periods - maturity_years * payments_per_year) > 1e-9:
        raise ValueError("maturity_years * payments_per_year must be an integer")
    return [i / payments_per_year for i in range(1, periods + 1)]


def par_swap_rate(
    curve: ZeroCurve,
    maturity_years: float,
    payments_per_year: int = 1,
) -> float:
    """Par fixed rate for a spot-start swap."""

    times = payment_times(maturity_years, payments_per_year)
    accrual = 1.0 / payments_per_year
    annuity = sum(accrual * curve.discount_factor(t) for t in times)
    return (1.0 - curve.discount_factor(maturity_years)) / annuity


def fixed_leg_pv(
    notional: float,
    fixed_rate: float,
    curve: ZeroCurve,
    maturity_years: float,
    payments_per_year: int,
) -> float:
    times = payment_times(maturity_years, payments_per_year)
    accrual = 1.0 / payments_per_year
    return notional * fixed_rate * sum(accrual * curve.discount_factor(t) for t in times)


def floating_leg_pv(notional: float, curve: ZeroCurve, maturity_years: float) -> float:
    """Floating leg PV approximation for spot-start par floater."""

    return notional * (1.0 - curve.discount_factor(maturity_years))


def swap_pv(swap: VanillaSwap, curve: ZeroCurve) -> float:
    """PV of the swap from the perspective of the swap holder."""

    fixed = fixed_leg_pv(
        notional=swap.notional,
        fixed_rate=swap.fixed_rate,
        curve=curve,
        maturity_years=swap.maturity_years,
        payments_per_year=swap.payments_per_year,
    )
    floating = floating_leg_pv(
        notional=swap.notional,
        curve=curve,
        maturity_years=swap.maturity_years,
    )

    if swap.pay_fixed:
        return floating - fixed
    return fixed - floating


def swap_pv01(swap: VanillaSwap, curve: ZeroCurve, bump_bp: float = 1.0) -> float:
    """PV change for a parallel bump in curve rates."""

    bumped_curve = curve.shifted(bump_bp)
    return swap_pv(swap, bumped_curve) - swap_pv(swap, curve)

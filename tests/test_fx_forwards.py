import pytest

from ing_fm.curves import ZeroCurve, parse_tenor
from ing_fm.fx_forwards import forward_rate, price_fx_forward


def test_fx_forward_pv_is_zero_at_fair_strike() -> None:
    spot = 1.10
    rd = 0.03
    rf = 0.01
    maturity = 1.5
    notional = 2_000_000

    fair_strike = forward_rate(spot=spot, domestic_rate=rd, foreign_rate=rf, maturity_years=maturity)
    pv = price_fx_forward(
        notional_base=notional,
        strike=fair_strike,
        spot=spot,
        domestic_rate=rd,
        foreign_rate=rf,
        maturity_years=maturity,
    )

    assert abs(pv) < 1e-8


def test_fx_forward_pv_sign_for_favorable_strike() -> None:
    spot = 1.08
    rd = 0.025
    rf = 0.01
    maturity = 1.0
    notional = 1_000_000

    fair_strike = forward_rate(spot=spot, domestic_rate=rd, foreign_rate=rf, maturity_years=maturity)
    better_strike = fair_strike - 0.015

    pv = price_fx_forward(
        notional_base=notional,
        strike=better_strike,
        spot=spot,
        domestic_rate=rd,
        foreign_rate=rf,
        maturity_years=maturity,
    )

    assert pv > 0


def test_fx_forward_uses_discount_curves() -> None:
    spot = 1.12
    maturity = 0.75
    domestic_curve = ZeroCurve.from_tenors(
        tenors=["3M", "6M", "1Y"],
        zero_rates=[0.020, 0.022, 0.024],
    )
    foreign_curve = ZeroCurve.from_tenors(
        tenors=["3M", "6M", "1Y"],
        zero_rates=[0.010, 0.011, 0.012],
    )

    fair = forward_rate(
        spot=spot,
        maturity_years=maturity,
        domestic_curve=domestic_curve,
        foreign_curve=foreign_curve,
    )
    expected = spot * foreign_curve.df(maturity) / domestic_curve.df(maturity)

    assert fair == pytest.approx(expected)


def test_fx_forward_changes_when_mid_tenor_changes() -> None:
    spot = 1.10
    maturity = 0.5
    domestic_curve_a = ZeroCurve.from_tenors(
        tenors=["1M", "3M", "6M", "1Y", "2Y"],
        zero_rates=[0.022, 0.023, 0.024, 0.025, 0.026],
    )
    domestic_curve_b = ZeroCurve.from_tenors(
        tenors=["1M", "3M", "6M", "1Y", "2Y"],
        zero_rates=[0.022, 0.023, 0.030, 0.025, 0.026],
    )
    foreign_curve = ZeroCurve.from_tenors(
        tenors=["1M", "3M", "6M", "1Y", "2Y"],
        zero_rates=[0.012, 0.013, 0.014, 0.015, 0.016],
    )

    fair_a = forward_rate(
        spot=spot,
        maturity_years=maturity,
        domestic_curve=domestic_curve_a,
        foreign_curve=foreign_curve,
    )
    fair_b = forward_rate(
        spot=spot,
        maturity_years=maturity,
        domestic_curve=domestic_curve_b,
        foreign_curve=foreign_curve,
    )

    assert fair_b > fair_a


def test_parse_tenor_common_cases() -> None:
    assert parse_tenor("1W") == pytest.approx(7.0 / 365.0)
    assert parse_tenor("1M") == pytest.approx(1.0 / 12.0)
    assert parse_tenor("6M") == pytest.approx(0.5)
    assert parse_tenor("1Y") == pytest.approx(1.0)

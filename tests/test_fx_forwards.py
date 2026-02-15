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

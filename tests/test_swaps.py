from fm_toolkit.curves import ZeroCurve
from fm_toolkit.swaps import VanillaSwap, par_swap_rate, swap_pv, swap_pv01


def test_par_swap_rate_gives_near_zero_pv() -> None:
    curve = ZeroCurve(
        times=[1, 2, 3, 5, 10], zero_rates=[0.02, 0.022, 0.024, 0.026, 0.028]
    )
    maturity = 5
    pay_freq = 2

    par = par_swap_rate(
        curve=curve, maturity_years=maturity, payments_per_year=pay_freq
    )
    swap = VanillaSwap(
        notional=5_000_000,
        fixed_rate=par,
        maturity_years=maturity,
        payments_per_year=pay_freq,
        pay_fixed=True,
    )

    pv = swap_pv(swap=swap, curve=curve)
    assert abs(pv) < 1e-6


def test_swap_pv01_sign_by_direction() -> None:
    curve = ZeroCurve(
        times=[1, 2, 3, 5, 10], zero_rates=[0.02, 0.022, 0.024, 0.026, 0.028]
    )

    payer = VanillaSwap(
        notional=10_000_000,
        fixed_rate=0.03,
        maturity_years=5,
        payments_per_year=2,
        pay_fixed=True,
    )
    receiver = VanillaSwap(
        notional=10_000_000,
        fixed_rate=0.03,
        maturity_years=5,
        payments_per_year=2,
        pay_fixed=False,
    )

    payer_pv01 = swap_pv01(swap=payer, curve=curve)
    receiver_pv01 = swap_pv01(swap=receiver, curve=curve)

    assert payer_pv01 > 0
    assert receiver_pv01 < 0

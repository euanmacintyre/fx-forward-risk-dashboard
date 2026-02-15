import pytest

from ing_fm.curves import ZeroCurve
from ing_fm.fx_forwards import forward_rate
from ing_fm.scenarios import fx_forward_scenarios


def test_fx_forward_scenarios_table_shape_and_names() -> None:
    domestic_curve = ZeroCurve.from_tenors(
        tenors=["1M", "3M", "6M", "1Y", "2Y"],
        zero_rates=[0.024, 0.025, 0.026, 0.027, 0.028],
    )
    foreign_curve = ZeroCurve.from_tenors(
        tenors=["1M", "3M", "6M", "1Y", "2Y"],
        zero_rates=[0.015, 0.016, 0.017, 0.018, 0.019],
    )

    df = fx_forward_scenarios(
        notional_base=5_000_000,
        strike=1.12,
        spot=1.10,
        maturity_years=1.0,
        domestic_curve=domestic_curve,
        foreign_curve=foreign_curve,
    )

    assert list(df.columns) == [
        "Scenario name",
        "Spot shock (pct)",
        "Domestic curve shock (bps)",
        "Foreign curve shock (bps)",
        "PV (domestic)",
        "PnL vs base",
    ]
    assert list(df["Scenario name"]) == [
        "Spot -1%",
        "Spot +1%",
        "Domestic +25bp",
        "Domestic -25bp",
        "Foreign +25bp",
        "Foreign -25bp",
        "Spot +1% & Domestic +25bp",
        "Spot -1% & Domestic -25bp",
    ]


def test_fx_forward_scenarios_spot_pnl_direction() -> None:
    spot = 1.10
    maturity = 1.0
    domestic_curve = ZeroCurve.from_tenors(
        tenors=["1M", "3M", "6M", "1Y", "2Y"],
        zero_rates=[0.024, 0.025, 0.026, 0.027, 0.028],
    )
    foreign_curve = ZeroCurve.from_tenors(
        tenors=["1M", "3M", "6M", "1Y", "2Y"],
        zero_rates=[0.015, 0.016, 0.017, 0.018, 0.019],
    )

    strike = forward_rate(
        spot=spot,
        maturity_years=maturity,
        domestic_curve=domestic_curve,
        foreign_curve=foreign_curve,
    )

    df = fx_forward_scenarios(
        notional_base=1_000_000,
        strike=strike,
        spot=spot,
        maturity_years=maturity,
        domestic_curve=domestic_curve,
        foreign_curve=foreign_curve,
    )

    spot_up_pnl = float(df.loc[df["Scenario name"] == "Spot +1%", "PnL vs base"].iloc[0])
    spot_down_pnl = float(df.loc[df["Scenario name"] == "Spot -1%", "PnL vs base"].iloc[0])

    assert spot_up_pnl > 0.0
    assert spot_down_pnl < 0.0
    assert abs(spot_up_pnl) == pytest.approx(abs(spot_down_pnl), rel=1e-4)

from fm_toolkit.curves import ZeroCurve
from fm_toolkit.report import build_fx_forward_client_note
from fm_toolkit.scenarios import fx_forward_scenarios


def test_build_fx_forward_client_note_contains_required_sections() -> None:
    domestic_curve = ZeroCurve.from_tenors(
        tenors=["1M", "3M", "6M", "1Y", "2Y"],
        zero_rates=[0.024, 0.025, 0.026, 0.027, 0.028],
    )
    foreign_curve = ZeroCurve.from_tenors(
        tenors=["1M", "3M", "6M", "1Y", "2Y"],
        zero_rates=[0.015, 0.016, 0.017, 0.018, 0.019],
    )
    scenario_df = fx_forward_scenarios(
        notional_base=5_000_000,
        strike=1.12,
        spot=1.10,
        maturity_years=1.0,
        domestic_curve=domestic_curve,
        foreign_curve=foreign_curve,
    )

    note = build_fx_forward_client_note(
        pair="EUR/USD",
        notional_base=5_000_000,
        maturity_years=1.0,
        strike=1.12,
        spot=1.10,
        domestic_curve=domestic_curve,
        foreign_curve=foreign_curve,
        scenario_df=scenario_df,
    )

    assert "## Trade Summary" in note
    assert "## Market Snapshot" in note
    assert "## Pricing Summary" in note
    assert "## Scenario Summary (Top 6)" in note
    assert "## Next Steps" in note
    assert "| Scenario name |" in note
    assert "Spot -1%" in note
    assert "Domestic +25bp" in note
    assert "Foreign +25bp" in note

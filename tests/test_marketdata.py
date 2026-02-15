import pytest

from fm_toolkit.marketdata import (
    FrankfurterProvider,
    SpotProvider,
    TwelveDataProvider,
    parse_pair,
)


def test_parse_pair_common_cases() -> None:
    assert parse_pair("EUR/USD") == ("EUR", "USD")
    assert parse_pair(" gbp/jpy ") == ("GBP", "JPY")

    with pytest.raises(ValueError):
        parse_pair("EURUSD")
    with pytest.raises(ValueError):
        parse_pair("EURO/USD")
    with pytest.raises(ValueError):
        parse_pair("")


def test_frankfurter_provider_mocked_response(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, object] = {}

    class MockResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {"date": "2026-02-15", "rates": {"USD": 1.105}}

    def fake_get(
        url: str, params: dict[str, str], timeout: tuple[float, float]
    ) -> MockResponse:
        captured["url"] = url
        captured["params"] = params
        captured["timeout"] = timeout
        return MockResponse()

    monkeypatch.setattr("fm_toolkit.marketdata.requests.get", fake_get)

    provider = FrankfurterProvider(timeout=(1.0, 2.0))
    spot, ts, source = provider.get_spot("EUR", "USD")

    assert captured["url"] == "https://api.frankfurter.dev/v1/latest"
    assert captured["params"] == {"base": "EUR", "symbols": "USD"}
    assert captured["timeout"] == (1.0, 2.0)
    assert spot == pytest.approx(1.105)
    assert ts == "2026-02-15"
    assert source == "Frankfurter"


def test_frankfurter_provider_inverts_when_inverse_exists(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[dict[str, str]] = []

    class MockResponse:
        def __init__(self, payload: dict[str, object]) -> None:
            self.payload = payload

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return self.payload

    def fake_get(
        url: str, params: dict[str, str], timeout: tuple[float, float]
    ) -> MockResponse:
        calls.append(params)
        if params == {"base": "EUR", "symbols": "USD"}:
            return MockResponse({"date": "2026-02-15", "rates": {}})
        if params == {"base": "USD", "symbols": "EUR"}:
            return MockResponse({"date": "2026-02-15", "rates": {"EUR": 0.8}})
        raise AssertionError(f"unexpected params: {params}")

    monkeypatch.setattr("fm_toolkit.marketdata.requests.get", fake_get)

    provider = FrankfurterProvider()
    spot, ts, source = provider.get_spot("EUR", "USD")

    assert calls == [
        {"base": "EUR", "symbols": "USD"},
        {"base": "USD", "symbols": "EUR"},
    ]
    assert spot == pytest.approx(1.25)
    assert ts == "2026-02-15"
    assert source == "Frankfurter (inverted)"


class _MockFallbackProvider(SpotProvider):
    def get_spot(self, base: str, quote: str) -> tuple[float, str, str]:
        return 1.2222, "2026-02-15T10:00:00Z", "MockFallback"


def test_twelvedata_falls_back_when_key_missing() -> None:
    provider = TwelveDataProvider(
        api_key=None, fallback_provider=_MockFallbackProvider()
    )

    spot, ts, source = provider.get_spot("EUR", "USD")

    assert spot == pytest.approx(1.2222)
    assert ts == "2026-02-15T10:00:00Z"
    assert source == "MockFallback (fallback)"


def test_twelvedata_inverts_when_direct_pair_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class MockResponse:
        def __init__(self, payload: dict[str, object]) -> None:
            self.payload = payload

        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return self.payload

    def fake_get(
        url: str, params: dict[str, str], timeout: tuple[float, float]
    ) -> MockResponse:
        if params["symbol"] == "EUR/USD":
            return MockResponse({"status": "error", "message": "pair not available"})
        if params["symbol"] == "USD/EUR":
            return MockResponse({"rate": "0.8000", "timestamp": 1739606400})
        raise AssertionError(f"unexpected params: {params}")

    monkeypatch.setattr("fm_toolkit.marketdata.requests.get", fake_get)

    provider = TwelveDataProvider(api_key="test-key")
    spot, ts, source = provider.get_spot("EUR", "USD")

    assert spot == pytest.approx(1.25)
    assert source == "Twelve Data (inverted)"
    assert ts.endswith("+00:00")

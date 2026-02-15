"""Live FX spot providers and pair parsing helpers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
import os

import requests

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()


_DEFAULT_TIMEOUT: tuple[float, float] = (3.05, 10.0)


def parse_pair(pair: str) -> tuple[str, str]:
    """Parse a pair like EUR/USD into (EUR, USD)."""

    if not pair:
        raise ValueError("pair must be non-empty and formatted as BASE/QUOTE")

    cleaned = pair.strip().upper()
    parts = cleaned.split("/")
    if len(parts) != 2:
        raise ValueError("pair must be formatted as BASE/QUOTE, e.g. EUR/USD")

    base, quote = parts[0].strip(), parts[1].strip()
    if len(base) != 3 or len(quote) != 3 or not base.isalpha() or not quote.isalpha():
        raise ValueError("base and quote must each be 3 alphabetic characters")

    return base, quote


class SpotProvider(ABC):
    """Abstract provider interface for spot FX rates."""

    @abstractmethod
    def get_spot(self, base: str, quote: str) -> tuple[float, str, str]:
        """Return (spot, timestamp, source)."""


class FrankfurterProvider(SpotProvider):
    """Spot provider backed by the Frankfurter API."""

    endpoint = "https://api.frankfurter.dev/v1/latest"

    def __init__(self, timeout: tuple[float, float] = _DEFAULT_TIMEOUT) -> None:
        self.timeout = timeout

    def get_spot(self, base: str, quote: str) -> tuple[float, str, str]:
        base, quote = parse_pair(f"{base}/{quote}")
        params = {"base": base, "symbols": quote}

        try:
            response = requests.get(self.endpoint, params=params, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise RuntimeError(f"Frankfurter request failed for {base}/{quote}: {exc}") from exc
        except ValueError as exc:
            raise RuntimeError(f"Frankfurter returned invalid JSON for {base}/{quote}: {exc}") from exc

        rates = payload.get("rates")
        if not isinstance(rates, dict) or quote not in rates:
            raise RuntimeError(f"Frankfurter response missing rate for {base}/{quote}")

        try:
            spot = float(rates[quote])
        except (TypeError, ValueError) as exc:
            raise RuntimeError(f"Frankfurter returned non-numeric rate for {base}/{quote}") from exc

        ts = str(payload.get("date") or datetime.now(timezone.utc).isoformat())
        return spot, ts, "Frankfurter"


class TwelveDataProvider(SpotProvider):
    """Spot provider backed by Twelve Data with Frankfurter fallback."""

    endpoint = "https://api.twelvedata.com/exchange_rate"

    def __init__(
        self,
        api_key: str | None = None,
        timeout: tuple[float, float] = _DEFAULT_TIMEOUT,
        fallback_provider: SpotProvider | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else os.getenv("TWELVEDATA_API_KEY")
        self.timeout = timeout
        self.fallback_provider = fallback_provider or FrankfurterProvider(timeout=timeout)

    def get_spot(self, base: str, quote: str) -> tuple[float, str, str]:
        base, quote = parse_pair(f"{base}/{quote}")
        pair = f"{base}/{quote}"

        if not self.api_key:
            return self._fallback(base, quote, "TWELVEDATA_API_KEY is not set")

        params = {"symbol": pair, "apikey": self.api_key}
        try:
            response = requests.get(self.endpoint, params=params, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            return self._fallback(base, quote, f"Twelve Data request failed for {pair}: {exc}")
        except ValueError as exc:
            return self._fallback(base, quote, f"Twelve Data returned invalid JSON for {pair}: {exc}")

        if str(payload.get("status", "")).lower() == "error":
            message = payload.get("message") or payload.get("code") or "unknown error"
            return self._fallback(base, quote, f"Twelve Data API error for {pair}: {message}")

        try:
            spot = float(payload["rate"])
        except (KeyError, TypeError, ValueError):
            return self._fallback(base, quote, f"Twelve Data response missing numeric rate for {pair}")

        ts = self._parse_timestamp(payload)
        return spot, ts, "Twelve Data"

    def _fallback(self, base: str, quote: str, reason: str) -> tuple[float, str, str]:
        try:
            spot, ts, source = self.fallback_provider.get_spot(base, quote)
            return spot, ts, f"{source} (fallback)"
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"{reason}. Fallback provider failed for {base}/{quote}: {exc}") from exc

    @staticmethod
    def _parse_timestamp(payload: dict[str, object]) -> str:
        raw = payload.get("timestamp")
        if isinstance(raw, (int, float)):
            return datetime.fromtimestamp(float(raw), tz=timezone.utc).isoformat()
        if isinstance(raw, str) and raw.strip():
            return raw

        raw_dt = payload.get("datetime")
        if isinstance(raw_dt, str) and raw_dt.strip():
            return raw_dt

        return datetime.now(timezone.utc).isoformat()


def get_live_spot(base: str, quote: str) -> tuple[float, str, str]:
    """Get spot with Twelve Data first and Frankfurter fallback."""

    provider = TwelveDataProvider()
    return provider.get_spot(base=base, quote=quote)

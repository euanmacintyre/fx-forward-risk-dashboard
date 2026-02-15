"""Zero-curve utilities for discounting and simple bumps."""

from __future__ import annotations

from dataclasses import dataclass
from math import exp
from typing import Sequence


@dataclass
class ZeroCurve:
    """Continuously-compounded zero curve with linear interpolation."""

    times: Sequence[float]
    zero_rates: Sequence[float]

    def __post_init__(self) -> None:
        self.times = tuple(float(t) for t in self.times)
        self.zero_rates = tuple(float(r) for r in self.zero_rates)

        if len(self.times) != len(self.zero_rates):
            raise ValueError("times and zero_rates must have the same length")
        if len(self.times) < 2:
            raise ValueError("curve requires at least two pillars")
        if any(t <= 0 for t in self.times):
            raise ValueError("all times must be positive")
        if list(self.times) != sorted(self.times):
            raise ValueError("times must be sorted ascending")

    @classmethod
    def flat(cls, rate: float, max_years: int = 10) -> "ZeroCurve":
        """Build a flat curve on annual pillars."""

        times = list(range(1, max_years + 1))
        rates = [rate] * len(times)
        return cls(times=times, zero_rates=rates)

    def zero_rate(self, t: float) -> float:
        """Interpolated zero rate for maturity t (in years)."""

        t = float(t)
        if t <= 0:
            raise ValueError("t must be positive")

        if t <= self.times[0]:
            return self.zero_rates[0]
        if t >= self.times[-1]:
            return self.zero_rates[-1]

        for idx in range(1, len(self.times)):
            if t <= self.times[idx]:
                t0, t1 = self.times[idx - 1], self.times[idx]
                r0, r1 = self.zero_rates[idx - 1], self.zero_rates[idx]
                weight = (t - t0) / (t1 - t0)
                return r0 + weight * (r1 - r0)

        return self.zero_rates[-1]

    def discount_factor(self, t: float) -> float:
        """Discount factor under continuous compounding."""

        rate = self.zero_rate(t)
        return exp(-rate * t)

    def shifted(self, bump_bp: float) -> "ZeroCurve":
        """Parallel shift in basis points."""

        shift = bump_bp * 1e-4
        return ZeroCurve(
            times=self.times,
            zero_rates=[r + shift for r in self.zero_rates],
        )

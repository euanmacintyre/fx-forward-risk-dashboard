#!/usr/bin/env python3
"""CLI demo for ING FM pricing."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SRC_PATH = Path(__file__).resolve().parents[1] / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from ing_fm.curves import ZeroCurve
from ing_fm.fx_forwards import forward_rate, price_fx_forward
from ing_fm.report import build_demo_report
from ing_fm.swaps import VanillaSwap, par_swap_rate, swap_pv, swap_pv01


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ING FM pricing demo CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("demo", help="Print combined demo report")

    fx_parser = subparsers.add_parser("fx-forward", help="Price an FX forward")
    fx_parser.add_argument("--notional", type=float, default=5_000_000)
    fx_parser.add_argument("--strike", type=float, default=1.12)
    fx_parser.add_argument("--spot", type=float, default=1.10)
    fx_parser.add_argument("--domestic-rate", type=float, default=0.03)
    fx_parser.add_argument("--foreign-rate", type=float, default=0.015)
    fx_parser.add_argument("--maturity", type=float, default=1.0)

    swap_parser = subparsers.add_parser("swap", help="Price a vanilla fixed-float swap")
    swap_parser.add_argument("--notional", type=float, default=10_000_000)
    swap_parser.add_argument("--fixed-rate", type=float, default=0.03)
    swap_parser.add_argument("--maturity", type=float, default=5.0)
    swap_parser.add_argument("--payments-per-year", type=int, default=2)
    swap_parser.add_argument("--pay-fixed", action="store_true")

    return parser


def run_fx_forward(args: argparse.Namespace) -> None:
    fair = forward_rate(
        spot=args.spot,
        domestic_rate=args.domestic_rate,
        foreign_rate=args.foreign_rate,
        maturity_years=args.maturity,
    )
    pv = price_fx_forward(
        notional_base=args.notional,
        strike=args.strike,
        spot=args.spot,
        domestic_rate=args.domestic_rate,
        foreign_rate=args.foreign_rate,
        maturity_years=args.maturity,
    )
    print(f"Fair forward: {fair:.6f}")
    print(f"PV (domestic): {pv:,.2f}")


def run_swap(args: argparse.Namespace) -> None:
    curve = ZeroCurve(times=[1, 2, 3, 5, 10], zero_rates=[0.02, 0.022, 0.024, 0.026, 0.028])
    par = par_swap_rate(
        curve=curve,
        maturity_years=args.maturity,
        payments_per_year=args.payments_per_year,
    )
    swap = VanillaSwap(
        notional=args.notional,
        fixed_rate=args.fixed_rate,
        maturity_years=args.maturity,
        payments_per_year=args.payments_per_year,
        pay_fixed=args.pay_fixed,
    )
    pv = swap_pv(swap=swap, curve=curve)
    pv01 = swap_pv01(swap=swap, curve=curve)
    print(f"Par rate: {par:.4%}")
    print(f"Swap PV: {pv:,.2f}")
    print(f"Swap PV01 (+1bp): {pv01:,.2f}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command in (None, "demo"):
        print(build_demo_report())
        return

    if args.command == "fx-forward":
        run_fx_forward(args)
        return

    if args.command == "swap":
        run_swap(args)
        return

    parser.error(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()

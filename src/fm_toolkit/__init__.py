"""FX & Rates pricing demo package."""

from .curves import ZeroCurve, parse_tenor
from .fx_forwards import forward_rate, price_fx_forward
from .marketdata import FrankfurterProvider, SpotProvider, TwelveDataProvider, get_live_spot, parse_pair
from .report import build_fx_forward_client_note
from .scenarios import fx_forward_scenarios
from .swaps import VanillaSwap, par_swap_rate, swap_pv, swap_pv01

__all__ = [
    "ZeroCurve",
    "parse_tenor",
    "parse_pair",
    "forward_rate",
    "price_fx_forward",
    "SpotProvider",
    "FrankfurterProvider",
    "TwelveDataProvider",
    "get_live_spot",
    "build_fx_forward_client_note",
    "fx_forward_scenarios",
    "VanillaSwap",
    "par_swap_rate",
    "swap_pv",
    "swap_pv01",
]

from __future__ import annotations
import os
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
import requests

_API_URL = os.getenv("EXCHANGE_RATE_API_URL", "https://open.er-api.com/v6")
BASE_CURRENCY = os.getenv("BASE_CURRENCY", "USD").upper()

_CACHE: dict[str, tuple[date, dict[str, Decimal]]] = {}


class RateUnavailable(Exception):
    """Raised when an exchange rate could not be fetched."""


def _today() -> date:
    return date.today()


def _fetch_rates(base: str) -> dict[str, Decimal]:
    url = f"{_API_URL.rstrip('/')}/latest/{base}"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    rates = data.get("rates")
    if not rates:
        raise RateUnavailable(f"No rates returned for base {base}")
    return {code: Decimal(str(value)) for code, value in rates.items()}


def _rates_for(base: str) -> dict[str, Decimal]:
    base = base.upper()
    cached = _CACHE.get(base)
    if cached and cached[0] == _today():
        return cached[1]
    rates = _fetch_rates(base)
    _CACHE[base] = (_today(), rates)
    return rates


def get_rate(from_currency: str, to_currency: str) -> Decimal:
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    if from_currency == to_currency:
        return Decimal("1")
    rates = _rates_for(to_currency)
    rate = rates.get(from_currency)
    if not rate or rate == 0:
        raise RateUnavailable(f"No rate for {from_currency}->{to_currency}")
    return Decimal("1") / rate


def convert(amount: Decimal, from_currency: str, to_currency: str) -> Decimal:
    rate = get_rate(from_currency, to_currency)
    return (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

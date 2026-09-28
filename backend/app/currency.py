"""Canonical KZT money conversion for the storefront and tests.

Rates are development configuration: KZT per one unit of the display currency.
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict

BASE_CURRENCY = "KZT"
KZT_PER_UNIT: Dict[str, Decimal] = {
    "KZT": Decimal("1"),
    "RUB": Decimal("5.2"),
    "USD": Decimal("500"),
}


def convert_from_kzt_tiyn(amount_tiyn: int, currency: str) -> Decimal:
    if amount_tiyn < 0:
        raise ValueError("amount must not be negative")
    code = currency.upper()
    rate = KZT_PER_UNIT.get(code)
    if rate is None or rate <= 0:
        raise ValueError("unsupported or invalid currency rate")
    amount_kzt = Decimal(amount_tiyn) / Decimal(100)
    places = Decimal("0.01") if code == "USD" else Decimal("1")
    return (amount_kzt / rate).quantize(places, rounding=ROUND_HALF_UP)


def format_money(amount_tiyn: int, currency: str) -> str:
    code = currency.upper()
    value = convert_from_kzt_tiyn(amount_tiyn, code)
    if code == "USD":
        return f"${value:,.2f}"
    symbol = {"KZT": "₸", "RUB": "₽"}[code]
    return f"{value:,.0f}".replace(",", " ") + f" {symbol}"

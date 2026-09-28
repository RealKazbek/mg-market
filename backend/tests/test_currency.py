from decimal import Decimal

import pytest

from app.currency import convert_from_kzt_tiyn, format_money


@pytest.mark.parametrize("kzt, rub, usd", [
    (1000, Decimal("2"), Decimal("0.02")),
    (10000, Decimal("19"), Decimal("0.20")),
    (100000, Decimal("192"), Decimal("2.00")),
    (1000000, Decimal("1923"), Decimal("20.00")),
])
def test_kzt_conversion_direction(kzt, rub, usd):
    assert convert_from_kzt_tiyn(kzt, "KZT") == Decimal(kzt) / 100
    assert convert_from_kzt_tiyn(kzt, "RUB") == rub
    assert convert_from_kzt_tiyn(kzt, "USD") == usd


def test_money_formatting_and_invalid_rates():
    assert format_money(2499000, "KZT") == "24 990 ₸"
    assert format_money(2499000, "RUB") == "4 806 ₽"
    assert format_money(2499000, "USD") == "$49.98"
    with pytest.raises(ValueError):
        convert_from_kzt_tiyn(-1, "KZT")
    with pytest.raises(ValueError):
        convert_from_kzt_tiyn(1000, "EUR")

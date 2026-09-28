"""Публичные метаданные витрины: категории и валюты."""
from typing import List

from fastapi import APIRouter

from .. import rates
from .. import repository as repo
from ..config import get_settings
from ..db import db_session

router = APIRouter(prefix="/api", tags=["meta"])

# Цены каталога хранятся в тиынах KZT. ISO-код оставляем для интеграций.
_CURRENCY_META = [
    {"code": "KZT", "symbol": "₸", "locale": "kk-KZ", "kzt_per_unit": 1.0},
    # Development snapshot: 1 RUB ≈ 5.2 KZT, 1 USD ≈ 500 KZT.
    {"code": "RUB", "symbol": "₽", "locale": "ru-RU", "kzt_per_unit": 5.2},
    {"code": "USD", "symbol": "$", "locale": "en-US", "kzt_per_unit": 500.0},
]


@router.get("/categories", response_model=List[str])
def list_categories():
    with db_session() as conn:
        return repo.list_categories(conn)


@router.get("/currencies")
def list_currencies():
    """Static demo rates from canonical KZT; not live market rates."""
    settings = get_settings()
    return {"base": "KZT", "currencies": _CURRENCY_META}

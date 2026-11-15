"""Small invoicing helpers. The behaviour is specified in README.md."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

CURRENCIES = ("EUR", "USD", "HUF", "GBP")


def split_amount(total_cents: int, weights: list[int]) -> list[int]:
    total_weight = sum(weights)
    return [round(total_cents * w / total_weight) for w in weights]


def business_days(start: date, end: date, holidays=()) -> int:
    n = 0
    d = start
    while d <= end:
        if d.weekday() < 5:
            n += 1
        d += timedelta(days=1)
    return max(n - len(holidays), 0)


def parse_amount(text: str) -> int:
    t = text.strip().upper()
    for code in CURRENCIES:
        t = t.replace(code, "")
    t = t.strip().replace(" ", "")
    negative = t.startswith("-")
    t = t.lstrip("-")
    if "," in t and "." in t:
        t = t.replace(".", "").replace(",", ".")
    elif "," in t:
        t = t.replace(",", ".")
    cents = int(Decimal(t) * 100)
    return -cents if negative else cents


def apply_discounts(subtotal_cents: int, discounts: list[tuple[str, int]]) -> int:
    amount = subtotal_cents
    for kind, value in discounts:
        if kind == "percent":
            amount = int(amount * (100 - value) / 100)
        else:
            amount -= value
    return amount


def late_fee(days_late: int, amount_cents: int) -> int:
    if days_late <= 0:
        return 0
    if days_late < 30:
        rate = 2
    elif days_late < 60:
        rate = 5
    else:
        rate = 10
    fee = round(amount_cents * rate / 100)
    return min(fee, 5000)

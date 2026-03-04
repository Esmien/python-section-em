from dataclasses import dataclass


@dataclass(frozen=True)
class Currency:
    name: str
    symbol: str

rub = Currency(name="RUB", symbol="₽")
usd = Currency(name="USD", symbol="$")
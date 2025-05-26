import enum
from dataclasses import dataclass

__all__ = ("AvailableCurrency", "Currency", "rub", "usd")


class AvailableCurrency(enum.Enum):
    RUB = enum.auto()
    USD = enum.auto()


@dataclass(slots=True, frozen=True, eq=True, repr=True)
class Currency:
    code: AvailableCurrency


@dataclass(slots=True, frozen=True, eq=True, repr=True)
class RUB(Currency):
    code: Currency = AvailableCurrency.RUB


@dataclass(slots=True, frozen=True, eq=True, repr=True)
class USD(Currency):
    code: Currency = AvailableCurrency.USD


rub = RUB()
usd = USD()

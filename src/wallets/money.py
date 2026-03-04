from dataclasses import dataclass
from src.wallets.currency import Currency
from src.wallets.exceptions import NotComparisonException, NegativeValueException


@dataclass
class Money:
    value: float
    currency: Currency

    def __add__(self, other: "Money") -> "Money":
        """ Суммирование денег в одной валюте """

        if self.currency != other.currency:
            raise NotComparisonException("Currencies are not the same")

        return Money(value=self.value + other.value, currency=self.currency)


    def __sub__(self, other: "Money") -> "Money":
        """ Вычитание денег в одной валюте """
        if self.currency != other.currency:
                raise NotComparisonException("Currencies are not the same")

        return Money(value=self.value - other.value, currency=self.currency)


class Wallet:
    """ Реализация кошелька с несколькими валютами """

    def __init__(self, *moneys: Money):
        self._data: dict[Currency, Money] = {}
        for m in moneys:
            self._data[m.currency] = m


    @property
    def currencies(self):
        """ Возвращает список валют в кошельке """

        return set(self._data.keys())


    def __getitem__(self, currency: Currency) -> Money:
        """ Возвращает данные из кошелька по выбранной валюте """

        return self._data.get(currency, Money(value=0, currency=currency))


    def __delitem__(self, currency: Currency):
        """ Удаляет данные из кошелька по выбранной валюте """

        self._data.pop(currency, None)


    def __len__(self) -> int:
        """ Возвращает количество валют в кошельке """

        return len(self._data)


    def __contains__(self, currency: Currency) -> bool:
        """ Проверяет наличие валюты в кошельке """

        return currency in self._data


    def add(self, money: Money) -> "Wallet":
        """ Добавляет деньги в кошелек """

        current = self._data.get(money.currency, Money(value=0, currency=money.currency))
        self._data[money.currency] = current + money
        return self  # возврат self нужен для цепочки .add().add()


    def sub(self, money: Money) -> "Wallet":
        """ Списывает деньги из кошелька """

        # Попытка списать деньги
        current = self._data.get(money.currency, Money(value=0, currency=money.currency))
        result = current - money

        # Проверка результата на отрицательное значение
        if result.value < 0:
            raise NegativeValueException("Недостаточно средств")

        # Обновление данных в кошельке
        self._data[money.currency] = result
        return self
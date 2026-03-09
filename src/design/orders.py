from dataclasses import dataclass, field
from abc import ABC, abstractmethod


LOYALTY_DISCOUNT: float = 5.0
FIXED_DISCOUNT: float = 500.0
PERCENT_DISCOUNT: float = 10.0


@dataclass
class Order:
    """ There is no need to describe anything here. """

    order_id: int
    base_total: float

    is_loyalty: bool = False
    promo_code: str | None = None

    final_total: float = field(init=False)


    def __post_init__(self):
        """ Вычисление итоговой суммы при инициализации до применения скидок. """

        self.final_total = self.base_total


class BaseDiscount(ABC):
    """ Базовый класс для всех видов скидок. """

    @abstractmethod
    def calculate_discount(self, order: Order) -> float:
        pass


class LoyaltyDiscount(BaseDiscount):
    """ Скидка за привилегии. """

    def calculate_discount(self, order: Order) -> float:
        """ Считает скидку за привилегии. """

        # Скидка в процентах от 0 до 100
        if 0 <= LOYALTY_DISCOUNT <= 100:
            return order.base_total * LOYALTY_DISCOUNT / 100

        return 0.0


class FixedDiscount(BaseDiscount):
    """ Фиксированная скидка. """

    def __init__(self, amount: float):
        if amount < 0:
            raise ValueError("Сумма скидки не может быть отрицательной")
        self.amount = amount


    def calculate_discount(self, order: Order) -> float:
        """ Считает скидку на фиксированную сумму. """

        return min(self.amount, order.base_total)


class PercentDiscount(BaseDiscount):
    """ Скидка в процентах. """

    def __init__(self, percent: float):
        if percent < 0 or percent > 100:
            raise ValueError("Процент скидки должен быть от 0 до 100")
        self.percent = percent


    def calculate_discount(self, order: Order) -> float:
        """ Считает скидку в процентах. """
        return order.base_total * (self.percent / 100)


class DiscountService:
    """ Сервис для применения скидок. """

    @staticmethod
    def _get_applicable_discount(order: Order) -> list[BaseDiscount]:
        """ Возвращает список примененных скидок. """
        discounts = []

        if order.is_loyalty:
            discounts.append(LoyaltyDiscount())

        if order.promo_code == "FIXED":
            discounts.append(FixedDiscount(FIXED_DISCOUNT))
        elif order.promo_code == "PERCENT":
            discounts.append(PercentDiscount(PERCENT_DISCOUNT))

        return discounts


    @classmethod
    def apply_discounts(cls, order: Order) -> None:
        """ Применение скидок к заказу. """

        # Получаем все скидки
        discounts = cls._get_applicable_discount(order)
        # Считаем сумму скидок
        total_discount = sum(discount.calculate_discount(order) for discount in discounts)

        # Применяем скидку к итоговой сумме, гарантируя неотрицательность
        order.final_total = max(order.base_total - total_discount, 0.0)
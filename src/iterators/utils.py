from dataclasses import dataclass, field
from itertools import batched
from typing import Iterable, TypeAlias

SomeRemoteData: TypeAlias = int


@dataclass
class Query:
    per_page: int = 3
    page: int = 1


@dataclass
class Page:
    per_page: int = 3
    results: Iterable[SomeRemoteData] = field(default_factory=list)
    next: int | None = None


def request(query: Query) -> Page:
    """ Имитирует запрос к удаленному API """

    # Создаем список из 10 элементов
    data = [i for i in range(0, 10)]
    # Разбиваем его на страницы, получаем список кортежей
    chunks = list(batched(data, query.per_page))
    # Если запрашиваемой страницы нет, возвращаем пустую страницу
    return Page(
        per_page=query.per_page,
        results=chunks[query.page - 1],
        next=query.page + 1 if query.page < len(chunks) else None,
    )


class RetrieveRemoteData:
    def __init__(self, per_page: int = 3):
        # Количество элементов на странице
        self.per_page = per_page

    def __iter__(self):
        # Начинаем с первой страницы
        current_page = 1

        # Крутим цикл, пока страницы не закончатся
        while current_page is not None:
            # Делаем запрос к API
            response = request(Query(per_page=self.per_page, page=current_page))

            # Поштучно отдаем элементы текущей страницы наружу
            yield from response.results

            # Забираем у API номер следующей страницы, если она есть
            current_page = response.next


# class Fibo:
#     def __init__(self, n: int) -> None:
#         if n < 0:
#             raise ValueError("Требуется положительное число")
#
#         self.n = n
#
#     def __iter__(self):
#         a, b = 0, 1

#         for _ in range(self.n):
#             yield a
#             a, b = b, a + b


class Fibo:
    def __init__(self, n: int) -> None:
        """ Инициализация итератора """

        if n < 0:
            raise ValueError("Требуется положительное число")
        self.n = n
        self.pos = 0
        self.a, self.b = 0, 1


    def __iter__(self):
        return self

    def __next__(self):
        """ Возвращает следующий элемент последовательности """

        # Проверка на конец последовательности
        if self.pos >= self.n:
            raise StopIteration

        current = self.a

        # Вычисление следующих значений и переход к следующему элементу
        self.a, self.b = self.b, self.a + self.b
        self.pos += 1

        return current

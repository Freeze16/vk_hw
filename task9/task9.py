from abc import ABC, abstractmethod
from typing import TypeVar, Callable, Iterable, List, Tuple, overload, Generic

T_Domain = TypeVar("T_Domain")
T_New = TypeVar("T_New")
T_Update = TypeVar("T_Update")

T = TypeVar("T")
S = TypeVar("S")

T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")


class AbstractRepository(ABC, Generic[T_Domain, T_New, T_Update]):

    @abstractmethod
    def create(self, data: T_New) -> T_Domain:
        pass

    @abstractmethod
    def update(self, item_id: int, data: T_Update) -> T_Domain:
        pass

    @abstractmethod
    def get(self) -> list[T_Domain]:
        pass

    @abstractmethod
    def delete(self, item: T_Domain) -> None:
        pass


def reduce_same_type(
        items: list[T],
        func: Callable[[T, T], T],
        initial: T | None = None
) -> T:
    """
    :param items: Список элементов типа T.
    :param func: Функция, принимающая аккумулятор (T) и следующий элемент (T),
                 возвращающая обновленный аккумулятор (T).
    :param initial: Опциональное начальное значение типа T.
    :return: Итоговый результат свертки типа T.
    """
    pass


def reduce_different_types(
        items: list[T],
        func: Callable[[S, T], S],
        initial: S
) -> S:
    """
    :param items: Список элементов типа T.
    :param func: Функция, принимающая аккумулятор (S) и следующий элемент (T),
                 возвращающая обновленный аккумулятор (S).
    :param initial: Начальное значение типа S (обязательно, так как типы не совпадают).
    :return: Итоговый результат свертки типа S.
    """
    pass


def zip_two(
        iter1: Iterable[T1],
        iter2: Iterable[T2]
) -> List[Tuple[T1, T2]]:
    pass


@overload
def zip(iter1: Iterable[T1], iter2: Iterable[T2]) -> List[Tuple[T1, T2]]:
    ...


@overload
def zip(
        iter1: Iterable[T1],
        iter2: Iterable[T2],
        iter3: Iterable[T3]
) -> List[Tuple[T1, T2, T3]]:
    ...


@overload
def zip(
        iter1: Iterable[T1],
        iter2: Iterable[T2],
        iter3: Iterable[T3],
        iter4: Iterable[T4]
) -> List[Tuple[T1, T2, T3, T4]]:
    ...


def zip(*iterables: Iterable) -> List[Tuple]:
    pass

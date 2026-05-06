from typing import Iterator, Any


class StackIsEmpty(Exception):
    def __init__(self, message="Стек пуст"):
        self.message = message
        super().__init__(self.message)


class Stack:
    def __init__(self) -> None:
        self._items = []

    def push(self, item: Any) -> None:
        self._items.append(item)

    def pop(self) -> Any:
        try:
            return self._items.pop()
        except IndexError:
            raise StackIsEmpty()

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator:
        return iter(self._items)

    def __contains__(self, value: Any) -> bool:
        return value in self._items

    def __getitem__(self, index: int) -> Any:
        return self._items[index]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Stack):
            return self._items == other._items

        return NotImplemented

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._items = []

    def __str__(self) -> str:
        return "Stack({})".format(", ".join(list(map(str, self._items))))

    def __repr__(self) -> str:
        return f"Stack({self._items})"

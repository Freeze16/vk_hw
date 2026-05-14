import sys
import weakref


class MockConnection:
    __slots__ = ('id', 'is_open', 'metadata')
    def __init__(self, id: int, is_open: bool = True, metadata: dict | None = None):
        self.id = id
        self.is_open = is_open
        self.metadata = metadata if metadata is not None else {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        self.is_open = False
        self.metadata.clear()


class ConnectionPool:
    def __init__(self):
        self._registry = weakref.WeakSet()

    def register(self, conn: MockConnection) -> None:
        self._registry.add(conn)

    def get_active(self) -> list[MockConnection]:
        return [conn for conn in self._registry if conn.is_open]


class GraphNode:
    def __init__(self, id: int, neighbors: list | None = None, meta: dict | None = None):
        self.id = id
        self.neighbors = neighbors if neighbors is not None else []
        self.meta = meta if meta is not None else {}


class OptimizedConnection:
    __slots__ = ("id", "is_open", "metadata")
    def __init__(self, id: int, is_open: bool = True, metadata: dict | None = None):
        self.id = id
        self.is_open = is_open
        self.metadata = metadata if metadata is not None else {}


def get_raw_refcount(obj: object) -> int:
    obj_address = id(obj)
    return ctypes.c_ssize_t.from_address(obj_address).value


def calculate_memory_diff() -> int:
    mock = MockConnection(id=1)
    optimized = OptimizedConnection(id=1)

    diff = sys.getsizeof(mock) - sys.getsizeof(optimized)
    return diff


def control_gc_cycles():
    gc.disable()

    node_a = GraphNode(1)
    node_b = GraphNode(2)

    node_a.neighbors.append(node_b)
    node_b.neighbors.append(node_a)

    node_a.meta["self"] = node_a
    node_b.meta["self"] = node_b

    ids = {id(node_a), id(node_b)}

    del node_a
    del node_b

    objs_in_heap = [obj for obj in gc.get_objects() if id(obj) in ids]
    print(f"Объектов в куче до gc.collect(): {len(objs_in_heap)}")

    gc.collect()

    gc.enable()

    objs_after = [obj for obj in gc.get_objects() if id(obj) in ids]
    print(f"Объектов в куче после gc.collect(): {len(objs_after)}")


def apply_gc_policy():
    gc.set_threshold(300, 8, 4)
    print(f"Новая политика GC: {gc.get_threshold()}")


def verify_weakset_behavior():
    pool = ConnectionPool()

    conn = MockConnection(id=42)
    pool.register(conn)

    del conn


def show_refcount_steps(obj: object) -> tuple[int, int, int]:
    step1 = sys.getrefcount(obj)
    ref = obj
    step2 = sys.getrefcount(obj)

    del ref
    step3 = sys.getrefcount(obj)

    return step1, step2, step3


if __name__ == "__main__":
    verify_weakset_behavior()
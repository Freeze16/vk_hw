import time
import functools
import collections


class NotAliveError(Exception):
    def __init__(self, message="Сервис не доступен"):
        self.message = message
        super().__init__(self.message)


def circuit_breaker(
        state_count: int,
        error_count: int,
        network_errors: list[type[Exception]],
        sleep_time_sec: int,
):
    if state_count <= 10:
        raise ValueError("Размер истории состояний (буфер) state_count должно быть > 10")
    if error_count >= 10:
        raise ValueError("Порог ошибок для блокировки error_count должно быть < 10")
    if sleep_time_sec < 0:
        raise ValueError("Время задержки после ошибки sleep_time_sec должно быть >= 0")

    def decorator(func):
        history = collections.deque(maxlen=state_count)
        errors = tuple(network_errors)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if len(history) >= error_count:
                if True not in list(history)[-error_count:]:
                    raise NotAliveError

            if history and not history[-1]:
                time.sleep(sleep_time_sec)

            try:
                res = func(*args, **kwargs)
                history.append(True)
                return res
            except errors:
                history.append(False)
                raise

        return wrapper

    return decorator

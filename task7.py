import weakref
import datetime
import dataclasses

import typing
from collections import deque


class UnknownUser(Exception):
    pass


@dataclasses.dataclass
class Session:
    user_id: int
    logged_in: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.now)
    logged_out: typing.Optional[datetime.datetime] = None


class SessionManager:
    def __init__(self) -> None:
        self._sessions: typing.Deque[Session] = deque()

    def open_session(self, user_id: int) -> Session:
        session = Session(user_id=user_id)
        self._sessions.append(session)
        return session

    def __del__(self) -> None:
        time_now = datetime.datetime.now()
        for session in self._sessions:
            if session.logged_out is None:
                session.logged_out = time_now


class SessionsCache:
    def __init__(self):
        self._hit_count = 0
        self._cache = weakref.WeakValueDictionary()

    @property
    def hit_count(self) -> int:
        return self._hit_count

    def get_session(self, user_id: int) -> Session:
        if user_id in self._cache:
            self._hit_count += 1
            return self._cache[user_id]

        session = Session(user_id=user_id)
        self._cache[user_id] = session
        return session

    def __len__(self) -> int:
        return len(self._cache)


class UserSessions:
    def __init__(self) -> None:
        self._user_id = None
        self._sessions = weakref.WeakSet()

    def add_session(self, session: Session) -> None:
        if self._user_id is None:
            self._user_id = session.user_id

        if session.user_id != self._user_id:
            raise UnknownUser(f"Expected user_id {self._user_id}, but got {session.user_id}")

        self._sessions.add(session)

    def __len__(self) -> int:
        return len(self._sessions)


if __name__ == '__main__':
    manager = SessionManager()

    session1 = manager.open_session(1)
    session2 = manager.open_session(2)

    assert session1.logged_out is None
    assert session2.logged_out is None

    del manager

    assert session1.logged_out is not None
    assert session2.logged_out is not None

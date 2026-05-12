import json
import heapq

from pathlib import Path
from functools import lru_cache
from collections import Counter
from typing import Any, Optional, Iterable


class LogEvent:
    def __init__(self, datetime: str, event_type: str, message: str, params: dict):
        self.datetime = datetime
        self.event_type = event_type
        self.message = message.format_map(params)
        self.params = params

    def __lt__(self, other):
        return self.datetime > other.datetime

    def __repr__(self):
        return f"[{self.datetime}] {self.event_type}: {self.message}"


class LogManager:
    BASE_DIR = Path(__file__).resolve().parent

    def __init__(self, path: str):
        user_path = (self.BASE_DIR / path.lstrip("/")).resolve()
        if not user_path.is_relative_to(self.BASE_DIR):
            raise ValueError("Access Denied")
        if not user_path.is_dir():
            raise NotADirectoryError(f"Directory not found: {user_path}")
        self.path = user_path

    @staticmethod
    def _get_events_stream(file_path: Path) -> Iterable[LogEvent]:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in reversed(lines):
                if not line.strip():
                    continue

                data = json.loads(line)
                yield LogEvent(
                    datetime=data['datetime'],
                    event_type=data['event_type'],
                    message=data['message'],
                    params=data.get('params', {})
                )

    def _merge_logs(self, files: List[Path], n: int, param_value: Optional[Any] = None) -> list[LogEvent]:
        if n <= 0:
            return []

        streams = [self._get_events_stream(f) for f in files]
        merged = heapq.merge(*streams)

        result = []
        for event in merged:
            if param_value is not None and param_value not in event.params.values():
                continue

            result.append(event)
            if len(result) >= n:
                break

        return result

    def tail(self, service_name: str, n: int) -> list[LogEvent]:
        files = sorted(self.path.glob(f"{service_name}_*.log"), reverse=True)
        return self._merge_logs(files, n)

    def tail_all(self, n: int) -> list[LogEvent]:
        files = sorted(self.path.glob("*.log"), key=lambda x: x.name.split('_')[-1], reverse=True)
        return self._merge_logs(files, n)

    def tail_param(self, value: Any, n: int) -> list[LogEvent]:
        files = sorted(self.path.glob("*.log"), key=lambda x: x.name.split('_')[-1], reverse=True)
        return self._merge_logs(files, n, param_value=value)

    @lru_cache(2048)
    def get_errors_count(self, start_time: str, end_time: str) -> Counter[str]:
        files = sorted(self.path.glob(f"*.log"), key=lambda x: x.name.split('_')[-1], reverse=True)
        file_range = [file for file in files if start_time <= file.name.split('_')[-1][:-4] <= end_time]

        stats = Counter()
        for file_path in file_range:
            service_name = file_path.name.split('_')[0]

            for event in self._get_events_stream(file_path):
                if event.datetime > end_time:
                    continue
                if event.datetime < start_time:
                    break

                if event.event_type == 'ERROR':
                    stats[service_name] += 1

        return stats

    @lru_cache(2048)
    def get_last_errors(self) -> dict[str, str]:
        files = sorted(self.path.glob(f"*.log"), key=lambda x: x.name.split('_')[-1], reverse=True)

        stats = {}
        for file_path in files:
            service_name = file_path.name.split('_')[0]
            if stats.get(service_name) is None:
                for event in self._get_events_stream(file_path):
                    if event.event_type == 'ERROR':
                        stats[service_name] = event.datetime
                        break

        return stats

import sys
import sysconfig

from hashlib import sha256
from threading import Lock
from multiprocessing import Manager
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

import logging
from typing import Dict, Union, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(threadName)s: %(message)s'
)
logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(self):
        self.results: Union[Dict[int, str], Manager.DictProxy[Any, Any]]  = {}

    @staticmethod
    def fetcher(task_id):
        return f"data_payload_{task_id}"

    @staticmethod
    def processor(data):
        for _ in range(1_000_000):
            data = sha256(data.encode()).hexdigest()
        return data

    def storer(self, task_id: int, data: str):
        self.results[task_id] = data

    def worker(self, task_id: int):
        data = self.fetcher(task_id)
        result = self.processor(data)
        self.storer(task_id, result)

    def run(self, tasks: list[int]):
        if not tasks: return

        with ThreadPoolExecutor(max_workers=10) as executor:
            list(executor.map(self.worker, tasks))


class SafePipeline(Pipeline):
    def __init__(self):
        super().__init__()
        self._lock = Lock()

    def storer(self, task_id: int, result: str) -> None:
        with self._lock:
            self.results[task_id] = result


class AdaptivePipeline(SafePipeline):
    def __init__(self):
        super().__init__()
        self.is_nogil = self._check_nogil()

        if not self.is_nogil:
            self._manager = Manager()
            self.results = self._manager.dict()
            logging.info("GIL is active. Using ProcessPoolExecutor strategy.")
        else:
            logging.info("Free-threading (NoGIL) detected. Using ThreadPoolExecutor strategy.")

    def _check_nogil(self):
        nogil_build = sysconfig.get_config_var("Py_GIL_DISABLED") == 1

        status_func = getattr(sys, "_is_gil_enabled", None)
        gil_enabled = status_func() if status_func else True

        return nogil_build or not gil_enabled

    def get_executor(self) -> Union[ThreadPoolExecutor, ProcessPoolExecutor]:
        if self.is_nogil:
            return ThreadPoolExecutor()

        return ProcessPoolExecutor()

    def run(self, tasks: list[int]):
        if not tasks: return

        with self.get_executor() as executor:
            list(executor.map(self.worker, tasks))

class RobustPipeline(AdaptivePipeline):
    def worker(self, task_id: int) -> None:
        try:
            super().worker(task_id)
        except Exception as e:
            logger.error(f"Task {task_id} failed with error: {e}", exc_info=True)

    def run(self, tasks: list[int]) -> None:
        logger.info(f"Starting robust pipeline with {len(tasks)} tasks.")
        super().run(tasks)
        logger.info(f"Pipeline finished. Total successful results: {len(self.results)}")


if __name__ == '__main__':
    pipeline = AdaptivePipeline()
    pipeline.run(list(range(5)))

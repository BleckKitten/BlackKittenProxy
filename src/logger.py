"""Logging helpers for the proxy."""

import logging
from typing import Optional

from interfaces import ILogger


class ProxyLogger(ILogger):
    def __init__(self, log_access_file: Optional[str], log_error_file: Optional[str], quiet: bool = False):
        self.quiet = quiet
        self.logger = logging.getLogger("blackkittenproxy")
        self.error_counter_callback = None
        self._setup_logging(log_access_file, log_error_file)

    def _setup_logging(self, log_access_file, log_error_file):
        class ErrorCounterHandler(logging.FileHandler):
            def __init__(self, counter_callback, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.counter_callback = counter_callback

            def emit(self, record):
                try:
                    if record.levelno >= logging.ERROR:
                        self.counter_callback()
                except Exception:
                    pass
                super().emit(record)

        if log_error_file:
            err = ErrorCounterHandler(self.increment_errors, log_error_file, encoding="utf-8")
            err.setFormatter(logging.Formatter("[%(asctime)s][%(levelname)s]: %(message)s", "%Y-%m-%d %H:%M:%S"))
            err.setLevel(logging.ERROR)
            err.addFilter(lambda r: r.levelno == logging.ERROR)
            error_handler = err
        else:
            error_handler = logging.NullHandler()

        if log_access_file:
            access_handler = logging.FileHandler(log_access_file, encoding="utf-8")
            access_handler.setFormatter(logging.Formatter("%(message)s"))
            access_handler.setLevel(logging.INFO)
            access_handler.addFilter(lambda r: r.levelno == logging.INFO)
        else:
            access_handler = logging.NullHandler()

        self.logger.propagate = False
        self.logger.handlers = []
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(access_handler)

    def set_error_counter_callback(self, callback):
        self.error_counter_callback = callback

    def increment_errors(self) -> None:
        if self.error_counter_callback:
            try:
                self.error_counter_callback()
            except Exception:
                pass

    def log_access(self, message: str) -> None:
        try:
            self.logger.info(message)
        except Exception:
            pass

    def log_error(self, message: str) -> None:
        try:
            self.logger.error(message)
        except Exception:
            pass

    def info(self, *a, **k) -> None:
        if not self.quiet:
            print(*a, **k)

    def error(self, *a, **k) -> None:
        if not self.quiet:
            print(*a, **k)

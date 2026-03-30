import logging
import sys

from rich.console import Console
from rich.logging import RichHandler


class Logger:
    _logger = logging.getLogger("advanced_mcp")
    _configured = False

    @classmethod
    def _configure(cls) -> None:
        if cls._configured:
            return

        handler = RichHandler(
            console=Console(file=sys.stderr),
            show_time=True,
            show_level=True,
            show_path=True,
            omit_repeated_times=False,
            markup=False,
            rich_tracebacks=True,
        )
        handler.setFormatter(logging.Formatter("%(message)s"))

        cls._logger.handlers.clear()
        cls._logger.addHandler(handler)
        cls._logger.setLevel(logging.INFO)
        cls._logger.propagate = False
        cls._configured = True

    @classmethod
    def info(cls, message: str) -> None:
        cls._configure()
        cls._logger.info(message, stacklevel=2)

    @classmethod
    def warn(cls, message: str) -> None:
        cls._configure()
        cls._logger.warning(message, stacklevel=2)

    @classmethod
    def debug(cls, message: str) -> None:
        cls._configure()
        cls._logger.debug(message, stacklevel=2)

    @classmethod
    def error(cls, message: str) -> None:
        cls._configure()
        cls._logger.error(message, stacklevel=2)

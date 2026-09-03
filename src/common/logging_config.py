import logging
import sys
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

HANDLER_NAME = "cora-run"

_NOISY_LOGGERS = ("urllib3", "requests", "charset_normalizer")


def configure_logging(
    script_name: str | None = None,
    level: int = logging.INFO,
    log_dir: str = "logs",
    backup_count: int = 5,
    when: str = "midnight",
    interval: int = 1,
    utc: bool = True,
) -> str:
    """
    Configure logging for a single run and return the path of the log file.

    Idempotent: calling it again leaves the existing configuration untouched.

    :param script_name: Base name of the log file, defaults to the running script.
    :return: The absolute path of the log file.
    """
    root = logging.getLogger()
    existing = _find_run_handler(root)
    if existing:
        return existing.baseFilename

    if script_name is None:
        script_name = Path(sys.argv[0]).stem

    Path(log_dir).mkdir(parents=True, exist_ok=True)

    handler = TimedRotatingFileHandler(
        filename=str(Path(log_dir) / f"{script_name}.log"),
        when=when,
        interval=interval,
        backupCount=backup_count,
        encoding="utf-8",
        utc=utc,
    )
    handler.set_name(HANDLER_NAME)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    root.addHandler(handler)
    root.setLevel(level)

    for name in _NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)

    return handler.baseFilename


def _find_run_handler(root: logging.Logger) -> TimedRotatingFileHandler | None:
    for handler in root.handlers:
        if handler.name == HANDLER_NAME and isinstance(
            handler, TimedRotatingFileHandler
        ):
            return handler
    return None

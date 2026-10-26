import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


MAX_LOG_BYTES = 1_000_000
BACKUP_COUNT = 3


def _log_directory() -> Path:
    if sys.platform == "win32":
        base_directory = Path(
            os.environ.get("LOCALAPPDATA")
            or os.environ.get("APPDATA")
            or Path.home() / "AppData" / "Local"
        )
        return base_directory / "AIFileConverter" / "Logs"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Logs" / "AIFileConverter"

    state_directory = Path(
        os.environ.get("XDG_STATE_HOME") or Path.home() / ".local" / "state"
    )
    return state_directory / "ai-file-converter" / "logs"


def configure_logging() -> Path:
    """Configure a rotating local application log and return its path."""
    log_directory = _log_directory()
    log_directory.mkdir(parents=True, exist_ok=True)
    log_path = log_directory / "application.log"
    logger = logging.getLogger()

    if any(
        isinstance(handler, RotatingFileHandler)
        and Path(handler.baseFilename) == log_path.resolve()
        for handler in logger.handlers
    ):
        return log_path

    handler = RotatingFileHandler(
        log_path,
        maxBytes=MAX_LOG_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return log_path

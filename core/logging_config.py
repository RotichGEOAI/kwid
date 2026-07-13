"""
core/logging_config.py
Centralized logging configuration. Every module fetches its logger via
`get_logger(__name__)` so log format/handlers stay consistent app-wide
and log level can be controlled centrally via the LOG_LEVEL env var.
"""
import logging
import logging.handlers
import os
import sys
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "kwid.log"

_LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

_FORMATTER = logging.Formatter(
    fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

_configured = False


def _configure_root():
    global _configured
    if _configured:
        return
    root = logging.getLogger("kwid")
    root.setLevel(_LOG_LEVEL)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(_FORMATTER)
    root.addHandler(stream_handler)

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(_FORMATTER)
    root.addHandler(file_handler)

    root.propagate = False
    _configured = True


def get_logger(name: str) -> logging.Logger:
    _configure_root()
    return logging.getLogger(f"kwid.{name}")

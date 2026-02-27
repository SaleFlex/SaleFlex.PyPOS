"""
SaleFlex.PyPOS - Centralized logging module.

Console output, file output, and log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
are all configurable via the [logging] section in settings.toml.
"""

import logging
import os
import sys
from pathlib import Path


# Supported log levels
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# Default values used when settings.toml is unavailable or incomplete
DEFAULT_LEVEL = "INFO"
DEFAULT_CONSOLE = True
DEFAULT_FILE = True
DEFAULT_LOG_DIR = "logs"
DEFAULT_LOG_FILE = "saleflex.log"


def _get_logging_config() -> dict:
    """Read the [logging] section from settings.toml and return it as a dict."""
    try:
        from settings.settings import Settings
        s = Settings()
        if hasattr(s, "setting_data") and s.setting_data:
            log_cfg = s.setting_data.get("logging")
            if isinstance(log_cfg, dict):
                return log_cfg
    except Exception:
        pass
    return {}


def _ensure_log_dir(log_path: str) -> None:
    """Create the parent directory for the log file if it does not exist."""
    try:
        parent = Path(log_path).parent
        if parent and not parent.exists():
            parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


def get_logger(name: str | None = None) -> logging.Logger:
    """
    Return a logger configured under the 'saleflex' root logger hierarchy.

    On the first call the root logger's handlers (console and/or file) are
    set up once; subsequent calls reuse the already-configured root logger.

    Args:
        name: Logger name, typically ``__name__`` of the calling module.
              When ``None`` the root logger 'saleflex' is returned.

    Returns:
        logging.Logger
    """
    logger_name = "saleflex" if not name else "saleflex." + str(name).strip(".")
    logger = logging.getLogger(logger_name)

    # Configure the root logger only once
    root = logging.getLogger("saleflex")
    if not root.handlers:
        cfg = _get_logging_config()
        level_name = (cfg.get("level") or DEFAULT_LEVEL).upper()
        level = LOG_LEVELS.get(level_name, logging.INFO)

        root.setLevel(level)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler
        if cfg.get("console", DEFAULT_CONSOLE):
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            console_handler.setFormatter(formatter)
            root.addHandler(console_handler)

        # File handler
        if cfg.get("file", DEFAULT_FILE):
            log_dir = cfg.get("log_dir") or DEFAULT_LOG_DIR
            log_file = cfg.get("log_file") or DEFAULT_LOG_FILE
            log_path = os.path.join(log_dir, log_file)
            _ensure_log_dir(log_path)
            try:
                file_handler = logging.FileHandler(log_path, encoding="utf-8")
                file_handler.setLevel(level)
                file_handler.setFormatter(formatter)
                root.addHandler(file_handler)
            except Exception:
                pass  # Silently skip if the log file cannot be created

    return logger

"""
SaleFlex.PyPOS - Point of Sale Application

Copyright (c) 2025-2026 Ferhat Mousavi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import atexit
import os
import sys

# ---------------------------------------------------------------------------
# Working directory – settings.toml, db.sqlite3, and logs/ are all resolved
# relative to the project root.  When the application is launched via a
# desktop shortcut, a service wrapper, or from a different directory the CWD
# may not point at the project root.  Fix it here, before any other import,
# so that every subsequent relative-path open succeeds.
# ---------------------------------------------------------------------------
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.getcwd() != _SCRIPT_DIR:
    os.chdir(_SCRIPT_DIR)

# ---------------------------------------------------------------------------
# Python version guard – the application requires Python 3.13 or higher.
# Fail fast with a clear message rather than letting an obscure import error
# surface later.
# ---------------------------------------------------------------------------
_MIN_PYTHON = (3, 13)
if sys.version_info < _MIN_PYTHON:
    sys.exit(
        f"SaleFlex.PyPOS requires Python {_MIN_PYTHON[0]}.{_MIN_PYTHON[1]} "
        f"or higher.\n"
        f"Current interpreter: Python {sys.version}"
    )

# ---------------------------------------------------------------------------
# Single-instance lock – a POS terminal must run only one instance at a time.
# A process-held file lock is used so the lock is automatically released if
# the process terminates unexpectedly (no manual cleanup needed on crash).
# ---------------------------------------------------------------------------
_LOCK_FILE_PATH = os.path.join(_SCRIPT_DIR, ".saleflex.lock")
_lock_fd = None


def _acquire_single_instance_lock() -> bool:
    """
    Try to acquire a file-based process lock.

    Returns True when the lock is acquired, False when another instance is
    already running.  The lock is held for the lifetime of the process and
    released automatically via the atexit handler.
    """
    global _lock_fd
    try:
        if sys.platform == "win32":
            import msvcrt
            _lock_fd = open(_LOCK_FILE_PATH, "wb")
            msvcrt.locking(_lock_fd.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            _lock_fd = open(_LOCK_FILE_PATH, "w")
            fcntl.flock(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        atexit.register(_release_single_instance_lock)
        return True
    except (IOError, OSError):
        try:
            if _lock_fd:
                _lock_fd.close()
        except Exception:
            pass
        _lock_fd = None
        return False


def _release_single_instance_lock() -> None:
    """Release the process lock and remove the lock file."""
    global _lock_fd
    if _lock_fd:
        try:
            if sys.platform == "win32":
                import msvcrt
                msvcrt.locking(_lock_fd.fileno(), msvcrt.LK_UNLCK, 1)
            _lock_fd.close()
        except Exception:
            pass
        _lock_fd = None
    try:
        os.unlink(_LOCK_FILE_PATH)
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if not _acquire_single_instance_lock():
        sys.exit(
            "SaleFlex.PyPOS is already running.\n"
            "Only one instance of the application can run at a time."
        )

    from core.logger import get_logger
    from settings.settings import Settings

    __version__ = Settings().app_version

    _logger = get_logger(__name__)
    _logger.info("=" * 60)
    _logger.info("Starting SaleFlex.PyPOS v%s", __version__)
    _logger.info("Python %s on %s", sys.version.split()[0], sys.platform)
    _logger.info("Working directory: %s", os.getcwd())
    _logger.info("=" * 60)

    try:
        from pos.manager import Application
        app = Application()
        app.run()
    except Exception:
        _logger.critical("Unhandled exception – application terminated", exc_info=True)
        sys.exit(1)
    finally:
        _logger.info("SaleFlex.PyPOS v%s – shutdown complete", __version__)

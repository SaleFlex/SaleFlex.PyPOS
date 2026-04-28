"""
SaleFlex.PyPOS - Point of Sale Application
Copyright (C) 2025-2026 Mousavi.Tech

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import atexit
import hashlib
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
_LOCK_MUTEX_NAME = (
    "Local\\SaleFlex.PyPOS."
    + hashlib.sha256(_SCRIPT_DIR.lower().encode("utf-8")).hexdigest()[:16]
)
_lock_fd = None
_lock_handle = None
_lock_registered = False


def _acquire_single_instance_lock() -> bool:
    """
    Try to acquire a file-based process lock.

    Returns True when the lock is acquired, False when another instance is
    already running.  The lock is held for the lifetime of the process and
    released automatically via the atexit handler.
    """
    global _lock_fd, _lock_handle, _lock_registered
    try:
        if sys.platform == "win32":
            import ctypes
            from ctypes import wintypes

            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.CreateMutexW.argtypes = (
                wintypes.LPVOID,
                wintypes.BOOL,
                wintypes.LPCWSTR,
            )
            kernel32.CreateMutexW.restype = wintypes.HANDLE

            ctypes.set_last_error(0)
            handle = kernel32.CreateMutexW(None, False, _LOCK_MUTEX_NAME)
            if not handle:
                raise OSError(ctypes.get_last_error(), "CreateMutexW failed")
            if ctypes.get_last_error() == 183:  # ERROR_ALREADY_EXISTS
                kernel32.CloseHandle(handle)
                return False

            _lock_handle = handle
            _lock_fd = open(_LOCK_FILE_PATH, "w", encoding="utf-8")
            _lock_fd.write(f"pid={os.getpid()}\n")
            _lock_fd.flush()
        else:
            import fcntl
            _lock_fd = open(_LOCK_FILE_PATH, "w")
            fcntl.flock(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            _lock_fd.write(f"pid={os.getpid()}\n")
            _lock_fd.flush()

        if not _lock_registered:
            atexit.register(_release_single_instance_lock)
            _lock_registered = True
        return True
    except (IOError, OSError):
        try:
            if _lock_fd:
                _lock_fd.close()
        except Exception:
            pass
        _lock_fd = None
        if _lock_handle:
            try:
                import ctypes

                ctypes.WinDLL("kernel32", use_last_error=True).CloseHandle(_lock_handle)
            except Exception:
                pass
            _lock_handle = None
        return False


def _release_single_instance_lock() -> None:
    """Release the process lock and remove the lock file."""
    global _lock_fd, _lock_handle
    if _lock_fd:
        try:
            if sys.platform != "win32":
                import fcntl

                fcntl.flock(_lock_fd, fcntl.LOCK_UN)
            _lock_fd.close()
        except Exception:
            pass
        _lock_fd = None

    if _lock_handle:
        try:
            import ctypes

            ctypes.WinDLL("kernel32", use_last_error=True).CloseHandle(_lock_handle)
        except Exception:
            pass
        _lock_handle = None

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
        _release_single_instance_lock()
        _logger.info("SaleFlex.PyPOS v%s – shutdown complete", __version__)

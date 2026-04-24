"""
SaleFlex.PyPOS - Office Push Worker

Background QThread that periodically forwards unsent completed transactions to
SaleFlex.OFFICE.  Runs in parallel to the main UI process so that network
latency or a temporarily unreachable OFFICE server never blocks the cashier.

Retry strategy
--------------
1. Every time a document is closed the push service is called immediately.
2. When the push fails (or no documents were closed), the worker waits
   *retry_interval_seconds* (default 3600 s = 1 hour) before trying again.
3. After a successful flush the timer resets to the configured interval.

Lifecycle (managed by the application startup):
    worker = OfficePushWorker()
    worker.start()     # QThread.start() → runs run() in background thread
    ...
    worker.stop()
    worker.wait()      # join before process exit

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

from __future__ import annotations

import threading

from PySide6.QtCore import QThread, Signal

from core.logger import get_logger

logger = get_logger(__name__)

# Default retry interval: 1 hour between automatic flush attempts.
_DEFAULT_RETRY_INTERVAL_SECONDS: int = 3600

# Module-level reference to the running worker so document_manager and other
# callers can request an immediate flush without knowing the Application object.
_active_worker: "OfficePushWorker | None" = None


def get_push_worker() -> "OfficePushWorker | None":
    """Return the running OfficePushWorker instance, or None if not started."""
    return _active_worker


def set_push_worker(worker: "OfficePushWorker | None") -> None:
    """Register (or clear) the module-level worker reference."""
    global _active_worker
    _active_worker = worker


class OfficePushWorker(QThread):
    """
    Background QThread that flushes the OFFICE push queue on a fixed schedule.

    Signals
    -------
    push_completed (bool):
        Emitted after each flush attempt.  True = all items sent, False = some failed.
    push_failed (str):
        Emitted when the flush raises an unexpected exception.  Carries the error message.
    """

    push_completed = Signal(bool)
    push_failed    = Signal(str)

    def __init__(
        self,
        retry_interval_seconds: int = _DEFAULT_RETRY_INTERVAL_SECONDS,
    ) -> None:
        super().__init__()
        self._interval   = retry_interval_seconds
        self._running    = False
        # Event used to wake the worker early (e.g. immediately after a
        # document is closed) without waiting for the full retry interval.
        self._wake_event = threading.Event()

    # ------------------------------------------------------------------
    # QThread entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Main loop executed in the background thread."""
        from pos.integration.office.office_push_service import OfficePushService

        if not OfficePushService.is_office_mode():
            logger.debug(
                "[OfficePushWorker] Not in 'office' mode – worker will not start."
            )
            return

        self._running = True
        set_push_worker(self)
        logger.info(
            "[OfficePushWorker] Started (retry_interval=%ds)", self._interval
        )

        while self._running:
            self._flush_cycle()
            # Wait for the retry interval or until wake() is called.
            # _wake_event.wait(1.0) sleeps at most 1 second per tick so the
            # thread can be stopped cleanly, but also wakes immediately when
            # a document is closed and wake() sets the event.
            self._wake_event.clear()
            for _ in range(self._interval):
                if not self._running:
                    break
                if self._wake_event.wait(timeout=1.0):
                    # wake() was called – exit the sleep loop immediately
                    logger.debug("[OfficePushWorker] Woken up early – flushing now")
                    self._wake_event.clear()
                    break

        set_push_worker(None)
        logger.info("[OfficePushWorker] Stopped")

    # ------------------------------------------------------------------
    # Public control
    # ------------------------------------------------------------------

    def stop(self) -> None:
        """Request a graceful stop.  Call wait() after this to join the thread."""
        self._running = False
        logger.info("[OfficePushWorker] Stop requested")

    def wake(self) -> None:
        """
        Ask the worker to flush pending items immediately without waiting for
        the next scheduled interval.

        Thread-safe: can be called from any thread (e.g. the main Qt thread
        after a document is closed).  The flush runs inside this QThread so
        the caller is never blocked.
        """
        self._wake_event.set()
        logger.debug("[OfficePushWorker] Wake signal sent")

    def trigger_immediate_flush(self) -> None:
        """Alias for wake() kept for backwards compatibility."""
        self.wake()

    # ------------------------------------------------------------------
    # Flush cycle
    # ------------------------------------------------------------------

    def _flush_cycle(self) -> None:
        """Attempt to push all pending / failed queue items to OFFICE."""
        try:
            from pos.integration.office.office_push_service import OfficePushService

            if not OfficePushService.has_pending():
                return

            logger.info("[OfficePushWorker] Flushing pending OFFICE push queue...")
            success = OfficePushService.flush_pending()
            self.push_completed.emit(success)

            if success:
                logger.info("[OfficePushWorker] Flush succeeded – all items sent")
            else:
                logger.warning(
                    "[OfficePushWorker] Flush partially or fully failed – "
                    "will retry in %d s", self._interval,
                )

        except Exception as exc:
            msg = str(exc)
            logger.error("[OfficePushWorker] Unexpected flush error: %s", msg)
            self.push_failed.emit(msg)

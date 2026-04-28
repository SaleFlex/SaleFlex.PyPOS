"""
SaleFlex.PyPOS - Background synchronisation worker.
Copyright (C) 2025-2026 Mousavi.Tech

Runs as a PySide6 QThread so the main UI thread is never blocked by network
operations.  Periodically calls GateSyncService.flush_pending_queue() to
push queued events and GatePullService to fetch updates and notifications.

Lifecycle (managed by Application.__init__ and Application.run):
    worker = SyncWorker()
    worker.start()          # QThread.start() → runs run() in background
    ...
    worker.stop()           # request graceful stop
    worker.wait()           # join thread before process exit

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

from __future__ import annotations

from PySide6.QtCore import QThread, Signal

from core.logger import get_logger
from core.exceptions import GATEConnectionError, GATESyncError

logger = get_logger(__name__)

# Default sync interval when not specified in settings.toml.
_DEFAULT_INTERVAL_SECONDS: int = 1800  # 30 minutes


class SyncWorker(QThread):
    """
    Background QThread that drives GATE synchronisation on a fixed schedule.

    Signals:
        sync_completed (str, bool): Emitted after each sync cycle.
                                    Args: connector_type, success.
        sync_failed    (str, str):  Emitted when a sync cycle raises an error.
                                    Args: connector_type, error_message.
        cache_refresh_needed (str): Emitted when a pull response indicates that
                                    a local cache must be rebuilt.
                                    Arg: cache_name ("product" | "campaign" | "price").
        message_received (str, str):Emitted when GATE delivers a terminal message.
                                    Args: title, body.
    """

    sync_completed       = Signal(str, bool)
    sync_failed          = Signal(str, str)
    cache_refresh_needed = Signal(str)
    message_received     = Signal(str, str)

    def __init__(self, interval_seconds: int = _DEFAULT_INTERVAL_SECONDS) -> None:
        super().__init__()
        self._interval = interval_seconds
        self._running = False

    # ------------------------------------------------------------------
    # QThread entry point
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Main loop executed in the background thread."""
        self._running = True
        logger.info("[SyncWorker] started (interval=%ds)", self._interval)

        while self._running:
            self._run_sync_cycle()
            # Use QThread.sleep() instead of time.sleep() to allow
            # the thread to be interrupted cleanly by stop().
            self.sleep(self._interval)

        logger.info("[SyncWorker] stopped")

    # ------------------------------------------------------------------
    # Public control
    # ------------------------------------------------------------------

    def stop(self) -> None:
        """Request a graceful stop.  Call wait() after this to join the thread."""
        self._running = False
        logger.info("[SyncWorker] stop requested")

    # ------------------------------------------------------------------
    # Sync cycle
    # ------------------------------------------------------------------

    def _run_sync_cycle(self) -> None:
        """Execute one full push + pull cycle."""
        self._push_cycle()
        self._pull_cycle()

    def _push_cycle(self) -> None:
        """Flush all pending outbox items to GATE."""
        try:
            from pos.integration.gate.gate_sync_service import get_default_gate_sync
            sync = get_default_gate_sync()
            if not sync.is_enabled():
                return
            sync.flush_pending_queue()
            self.sync_completed.emit("gate", True)
        except (GATEConnectionError, GATESyncError) as e:
            logger.warning("[SyncWorker] push cycle failed: %s", e)
            self.sync_failed.emit("gate", str(e))
        except Exception as e:
            logger.error("[SyncWorker] unexpected error in push cycle: %s", e)
            self.sync_failed.emit("gate", str(e))

    def _pull_cycle(self) -> None:
        """Fetch updates and notifications from GATE."""
        try:
            from pos.integration.gate.gate_pull_service import get_default_gate_pull
            from pos.integration.gate.serializers.notification_serializer import (
                NotificationSerializer,
            )

            pull = get_default_gate_pull()
            if not pull.is_enabled():
                return

            try:
                pull.pull_product_updates()
                pull.pull_campaign_updates()

                notifications = pull.pull_notifications()
                for notif in notifications:
                    notif_type = notif.get("type", "")
                    if NotificationSerializer.requires_cache_refresh(notif_type):
                        self.cache_refresh_needed.emit(notif_type.replace("_update", ""))
                    elif notif_type == "terminal_message":
                        self.message_received.emit(
                            notif.get("title", ""),
                            notif.get("body", ""),
                        )
            finally:
                from pos.service.campaign.active_campaign_cache import ActiveCampaignCache

                ActiveCampaignCache.reload_safely()

        except (GATEConnectionError,) as e:
            logger.warning("[SyncWorker] pull cycle failed: %s", e)
        except Exception as e:
            logger.error("[SyncWorker] unexpected error in pull cycle: %s", e)
